# Our Kitchen - hosting and install

**Hosted address:** _(fill in once deployed; always install from this same address)_


The contents of `src/` are a complete installable web app (PWA). All data is stored on the
phone itself (IndexedDB), it works offline, and it never needs Claude or any account.

FILES (keep them together in one folder, uploaded from src/)
  index.html, sw.js, manifest.webmanifest, icon-192.png, icon-512.png, icon-maskable-512.png,
  and the fonts/ folder (two .woff2 files). Upload the whole src/ folder including fonts/.

HOW TO PUT IT ON YOUR ANDROID PHONE
1. Host this folder on any HTTPS static host (a PWA will not install from a file or plain http).
   Easiest options (all free, drag-and-drop or upload a folder):
   - Netlify: https://app.netlify.com/drop  (create a free account so the site doesn't expire)
   - Cloudflare Pages: Workers & Pages > Create > Pages > Upload assets
   - GitHub Pages: put these files in a repo and enable Pages
2. On the phone, open the site's address in Chrome.
3. Tap the menu (three dots) > "Install app" (or "Add to Home screen"). Open it from the new icon.
4. In the app: Settings (gear) > set household size and any ingredients to avoid.

KEEPING YOUR DATA SAFE
- Data lives only on that phone. Clearing Chrome's site data or uninstalling the app erases it.
- Settings > "Share / save backup" creates a file. Do this every few weeks.
- To move to a new phone or share with your wife: make a backup, send the file, and use
  Settings > "Restore from backup" there (Merge or Replace).
- Keep using the SAME web address. Data is tied to the address, so a different host/URL starts empty
  (restore from a backup file to bring it over).

UPDATING THE APP
- Re-upload the folder to the same host. If you change index.html, also change VERSION in sw.js
  (e.g. 'ourkitchen-v3') so phones pick up the new version.

NOTES
- "Search online" uses TheMealDB (free community recipe database) and needs internet.
- "Paste a recipe" parses text you copy from any web page; you review it before saving.
