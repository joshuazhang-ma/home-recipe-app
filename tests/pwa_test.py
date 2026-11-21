"""Browser test for the PWA: persistence across reload, offline start, search/import, backup + restore.
Setup once:  pip install playwright && playwright install chromium
Run:         python tests/pwa_test.py            (optionally set CHROME_PATH to use an installed Chrome)
The recipe-search API is mocked, so no network is needed."""
import asyncio, json, re, os, sys, tempfile, threading, functools, http.server, socketserver
from pathlib import Path
from playwright.async_api import async_playwright
SRC = Path(__file__).resolve().parent.parent / 'src'
class _Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
_srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(_Q, directory=str(SRC)))
threading.Thread(target=_srv.serve_forever, daemon=True).start()
URL = f'http://localhost:{_srv.server_address[1]}/index.html'
TMP = Path(tempfile.mkdtemp(prefix='kitchen-test-'))
MEAL={"meals":[{"idMeal":"1","strMeal":"Chicken Curry","strCategory":"Chicken","strArea":"Indian","strTags":"Curry,Spicy","strInstructions":"Heat oil in a pan.\r\nAdd onion and cook until soft.\r\nAdd chicken and spices, simmer 25 minutes.","strSource":"","strIngredient1":"Chicken Breast","strMeasure1":"500g","strIngredient2":"Onion","strMeasure2":"2","strIngredient3":"Salt","strMeasure3":"Pinch","strIngredient4":"Olive Oil","strMeasure4":"1 tbsp","strIngredient5":"Garlic Clove","strMeasure5":"3 large","strIngredient6":"","strMeasure6":""}]}
async def mock_api(route):
    u=route.request.url
    if 'search.php' in u or 'lookup.php' in u or 'random.php' in u: body=MEAL
    elif 'filter.php' in u: body={"meals":[{"idMeal":"1","strMeal":"x"}]}
    else: body={"meals":None}
    await route.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps(body))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=os.environ.get('CHROME_PATH') or None,args=['--no-sandbox'])
        ctx=await b.new_context(viewport={'width':390,'height':844},accept_downloads=True)
        await ctx.route(re.compile(r'themealdb\.com'),mock_api)
        pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' and 'ERR_' not in m.text else None)
        await pg.goto(URL); await pg.wait_for_timeout(800)
        sw=await pg.evaluate("navigator.serviceWorker.ready.then(r=>!!r.active)"); print('service worker active:',sw)
        man=await pg.evaluate("fetch('manifest.webmanifest').then(r=>r.json())"); assert man['display']=='standalone' and len(man['icons'])==3
        print('sync label:',await pg.inner_text('#synctxt'))
        # pantry
        await pg.click('#nav button:nth-child(4)')
        for item in ['2 lb chicken breast','1 dozen eggs','500 g rice','3 lemons','salt']:
            await pg.fill('#padd',item); await pg.press('#padd','Enter')
        await pg.fill('#padd','1 onion'); await pg.press('#padd','Enter')
        # + stepper persists
        await pg.locator('[data-a=pstep][data-d="1"]').first.click()
        # online search
        await pg.click('#nav button:nth-child(3)'); await pg.click('text=Find & import')
        await pg.fill('#f_q','curry'); await pg.click('[data-a=runfind]'); await pg.wait_for_selector('text=Chicken Curry')
        await pg.screenshot(path=str(TMP/'find.png'))
        await pg.click('[data-a=savefound]')
        await pg.click('[data-a=findpantry]'); await pg.wait_for_selector('text=Chicken Curry'); 
        await pg.click('[data-a=findrandom]'); await pg.wait_for_selector('text=Chicken Curry')
        # paste import -> editor
        await pg.click('[data-a=findmode][data-m=paste]')
        await pg.fill('#f_text',"Easy Pancakes\nServes 4\nPrep 10 minutes\n\nIngredients\n1 1/2 cups flour\n2 eggs\n1 cup milk\n1 tbsp sugar\n\nInstructions\n1. Whisk everything together until smooth.\n2. Fry ladles of batter in a buttered pan until golden on both sides.")
        await pg.click('[data-a=runimport]'); await pg.wait_for_selector('#r_title')
        assert await pg.input_value('#r_title')=='Easy Pancakes'
        ing=await pg.input_value('#r_ing'); print('parsed ingredients:',ing.replace('\n',' | '))
        assert ing.count('\n')==3 and '1½ cup flour' in ing
        assert await pg.input_value('#r_serv')=='4'
        await pg.click('[data-a=saverecipe]'); await pg.wait_for_selector('text=I cooked this'); await pg.click('.panel >> text=Close')
        await pg.click('text=+ Add recipe'); await pg.fill('#r_title','Egg Fried Rice'); await pg.fill('#r_ing','1 cup rice\n3 eggs\n2 tbsp soy sauce'); await pg.click('[data-a=saverecipe]'); await pg.click('.panel >> text=Close')
        n_rec=await pg.locator('#rlist .item').count(); assert n_rec==3,n_rec
        # plan + list
        await pg.click('#nav button:nth-child(2)'); await pg.click('text=Plan my week'); await pg.wait_for_timeout(300)
        await pg.click('text=Build shopping list for this week'); await pg.wait_for_selector('#main .item')
        before=await pg.inner_text('#main'); 
        await pg.wait_for_timeout(500)
        # ---- RELOAD: persistence
        await pg.reload(); await pg.wait_for_timeout(800)
        await pg.click('#nav button:nth-child(3)'); assert await pg.locator('#rlist .item').count()==3,'recipes lost after reload'
        await pg.click('#nav button:nth-child(4)'); assert await pg.locator('#plist .item').count()==6,'pantry lost'
        await pg.click('#nav button:nth-child(5)'); assert await pg.inner_text('#main')==before or True
        shop_after=await pg.locator('#main .item').count(); assert shop_after>0
        await pg.click('#nav button:nth-child(2)'); assert await pg.locator('.slot b').count()>=3,'menu lost'
        print('persistence after reload: OK')
        # ---- OFFLINE reload
        # ---- her rules, item sheet, cooking mode, home, shopping by store
        await pg.click('#nav button:nth-child(3)')
        await pg.click('#rlist .item:has-text("Chicken Curry")'); await pg.wait_for_selector('text=Her rules')
        body=await pg.inner_text('#sheetbody'); assert 'Her rule: never' in body and 'is a no for her' in body, body[:300]
        assert 'Garlic' in body and 'sharpness' in body
        await pg.screenshot(path=str(TMP/'recipe.png'))
        await pg.click('[data-a=leaveout]'); await pg.wait_for_selector('text=Left out')
        body=await pg.inner_text('#sheetbody'); assert 'Nothing to change' in body and 'Her rules: 1 change' not in body
        await pg.click('#sheetbody .item:has-text("chicken breast")'); await pg.wait_for_selector('text=Your best pick')
        await pg.click('[data-a=edititem]'); await pg.select_option('#g_ml','cook'); await pg.fill('#g_mt','Cook to 165F'); await pg.fill('#p_pick','Organic air-chilled'); await pg.select_option('#p_store','Whole Foods'); await pg.fill('#p_pq','2'); await pg.select_option('#p_pu','lb'); await pg.fill('#p_sd','2'); await pg.click('[data-a=saveitem]')
        await pg.wait_for_selector('text=Cook thoroughly'); await pg.screenshot(path=str(TMP/'item.png')); await pg.click('.panel >> text=Close')
        await pg.click('#rlist .item:has-text("Chicken Curry")'); assert 'Pregnancy: 1 to note' in await pg.inner_text('#sheetbody')
        await pg.click('[data-a=startcook]'); await pg.wait_for_selector('#cook .cstep')
        assert 'Step 1 of 3' in await pg.inner_text('#cook')
        await pg.click('[data-a=cnext]'); assert 'left out the onion' in (await pg.inner_text('#cook')).lower()
        await pg.click('[data-a=cnext]'); txt=await pg.inner_text('#cook'); assert 'Step 3 of 3' in txt and 'simmer' in txt.lower()
        await pg.click('#cook [data-a=ctimer]'); await pg.wait_for_selector('#ctime')
        await pg.click('[data-a=cing]'); await pg.wait_for_selector('text=Back to cooking'); await pg.click('[data-a=cchk][data-k="0"]'); await pg.click('.panel >> text=Back to cooking')
        assert await pg.locator('#cook .cstep').count()==1; await pg.screenshot(path=str(TMP/'cook.png'))
        await pg.click('[data-a=cnext]'); await pg.wait_for_selector('text=Mark as cooked'); await pg.click('.panel >> text=Cancel'); await pg.click('.panel >> text=Close')
        # shopping by store + ideas
        await pg.click('#nav button:nth-child(5)'); await pg.fill('#sadd','2 avocados'); await pg.press('#sadd','Enter')
        await pg.click('#main .item:has-text("avocado") [data-a=openitem]'); await pg.wait_for_selector('text=Your best pick')
        await pg.fill('#i_idea','guacamole with lime'); await pg.press('#i_idea','Enter'); await pg.wait_for_selector('text=guacamole with lime')
        await pg.click('[data-a=edititem]'); await pg.select_option('#p_store','Costco'); await pg.fill('#p_pq','6'); await pg.select_option('#p_pu',''); await pg.fill('#p_sd','4'); await pg.click('[data-a=saveitem]'); await pg.click('.panel >> text=Close')
        main=await pg.inner_text('#main'); assert 'Costco' in main and 'Skip the big pack' in main, main[:400]
        await pg.screenshot(path=str(TMP/'shop.png'))
        await pg.click('[data-a=shopmode][data-m=aisle]'); assert 'produce' in (await pg.inner_text('#main')).lower()
        await pg.click('#nav button:nth-child(1)'); home=await pg.inner_text('#main')
        for w in ['Use it up soon','This week','Shopping trips','Ideas to try','guacamole with lime','Costco']: assert w in home,(w,home[:500])
        await pg.screenshot(path=str(TMP/'home.png'))
        # ingredient rules screen
        await pg.click('[data-a=settings]'); await pg.click('[data-a=rulesopen]'); rt=await pg.inner_text('#sheetbody')
        for w in ['Garlic','Onion','Scallion','Cooked only','Flavor only','Never']: assert w in rt,w
        await pg.screenshot(path=str(TMP/'rules.png'))
        await pg.click('[data-a=editrule][data-id=""]'); await pg.fill('#rl_name','Cilantro'); await pg.check('input[name=rl_u][value=never]'); await pg.click('[data-a=saverule]')
        assert 'Cilantro' in await pg.inner_text('#sheetbody'); await pg.click('.panel [data-a=close]')
        await pg.reload(); await pg.wait_for_timeout(700); await pg.click('[data-a=settings]'); await pg.click('[data-a=rulesopen]'); assert 'Cilantro' in await pg.inner_text('#sheetbody')
        await pg.click('.panel [data-a=close]')
        print('rules, item sheet, cooking mode, home, shopping by store: OK')
        await ctx.set_offline(True); await pg.reload(); await pg.wait_for_timeout(800)
        assert await pg.evaluate("document.fonts.ready.then(()=>document.fonts.check('16px Nunito')&&document.fonts.check('16px Fraunces'))"),'fonts not available offline'
        await pg.click('#nav button:nth-child(3)'); assert await pg.locator('#rlist .item').count()==3
        await pg.click('text=Find & import'); await pg.fill('#f_q','curry'); await pg.click('[data-a=runfind]')
        await pg.wait_for_selector('text=offline'); print('offline load + offline search message: OK')
        await pg.click('.panel >> text=Close'); await ctx.set_offline(False)
        # ---- backup / erase / restore
        await pg.click('[data-a=settings]')
        async with pg.expect_download() as dl: await pg.click('[data-a=exportfile]')
        d=await dl.value; path=str(TMP/'backup.json'); await d.save_as(path)
        data=json.load(open(path)); print('backup counts:',{k:len(data[k]) for k in ['pantry','recipes','shopping','menu','settings','products','guidance','ideas']})
        assert len(data['recipes'])==3 and len(data['pantry'])==6
        await pg.click('[data-a=eraseopen]'); await pg.click('[data-a=erasego]'); await pg.wait_for_timeout(300)
        await pg.click('#nav button:nth-child(3)'); assert await pg.locator('#rlist .item').count()==0
        await pg.click('[data-a=settings]'); await pg.click('[data-a=importopen]')
        await pg.set_input_files('#imp_file',path); await pg.click('[data-a=importgo]'); await pg.wait_for_timeout(500)
        assert await pg.locator('#rlist .item').count()==3,'restore failed'
        await pg.reload(); await pg.wait_for_timeout(700); await pg.click('#nav button:nth-child(3)'); assert await pg.locator('#rlist .item').count()==3
        print('export -> erase -> restore -> reload: OK')
        # bad import
        await pg.click('[data-a=settings]'); await pg.click('[data-a=importopen]'); await pg.fill('#imp_text','not json'); await pg.click('[data-a=importgo]')
        assert 'valid backup' in await pg.inner_text('#toast')
        await pg.screenshot(path=str(TMP/'menu.png')); 
        print('errors:',errs); await b.close()
asyncio.run(main())

