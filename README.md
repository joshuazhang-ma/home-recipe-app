# home-recipe-app

> One-sentence purpose: a private Android app for our household that tracks the pantry, remembers our recipes, plans a weekly menu around what we already have, and builds the shopping list.

- **Category:** 01_apps
- **Created:** 2026-11-21
- **Status:** building   <!-- idea | building | working | maintenance | dormant -->

## What it does
"Our Kitchen" is an installable web app (PWA) for Android Chrome. It keeps the pantry, recipes, weekly menu and shopping list on the phone itself (IndexedDB), works offline, and needs no account or server. The menu planner prefers recipes we can mostly cook from the pantry, and the shopping list is the week's ingredients minus what is on hand, grouped by the store where we buy each item. It also follows household ingredient rules (for example onion never, garlic cooked and hidden), shows pregnancy guidance at decision time, advises when a bigger pack is worth it, and walks through a recipe step by step in cooking mode. Look: warm and homey (design brief in `docs/design.md`).

## How to run
```
# Preview on this PC (any static server works; needs Python or the py launcher)
scripts\serve.cmd                  ->  open http://localhost:8080

# Tests (once: pip install playwright ; playwright install chromium)
node tests\logic.test.js           # parsing, matching, shopping-list maths, ingredient rules, buying advice
python tests\pwa_test.py           # reload persistence, offline start (incl. fonts), search/import, rules, cooking mode, shopping by store, backup/restore

# Put it on the phone
Upload the CONTENTS of src\ to any HTTPS static host (Netlify, Cloudflare Pages, GitHub Pages),
open that address in Chrome on the phone, menu > Install app.
Full steps: docs\hosting-and-install.md
```
If you change anything in `src\`, bump `VERSION` in `src\sw.js` so installed phones pick up the update.

## Folder map
| Path | Purpose |
|------|---------|
| `docs/` | design notes and decisions, hosting + install steps |
| `src/` | the app: `index.html` (UI + logic), `sw.js` (offline), `manifest.webmanifest`, icons, `fonts/` (Fraunces and Nunito, bundled so it works offline). This folder is exactly what gets deployed |
| `data/` | sample backups for testing restore (private files are git-ignored) |
| `assets/` | icon source art, screenshots |
| `scripts/` | `serve.cmd` local preview |
| `tests/` | `logic.test.js` (node), `pwa_test.py` (Playwright) |

## v1 scope (what "finished" means for this project)
- Home dashboard: tonight's dinner, use-it-up list (best-before dates with the planned recipe or a freeze tip), week at a glance, shopping trips by store, ideas to try
- Pantry: quick-add ("2 lb chicken"), +/- quantities, units, aisle category, best-before dates, staples
- Recipes: add/edit/delete, favorites, scaling to household size, on-hand indicators, "I cooked this" deducts the pantry
- Recipe discovery: online search (TheMealDB) and paste-a-recipe import, both with a review step
- Weekly menu: plan Mon-Sun around the pantry, lock or skip meals, ingredient avoid-list, household size
- Shopping list: built from the menu minus the pantry, grouped by store (or by aisle), "done shopping" moves items into the pantry
- Item sheet (tap any ingredient): preferred product and store, pack size and how long it keeps, ideas to try, pregnancy guidance (medical and traditional)
- Buying advice on the shopping list: one pack covers it, bulk ok, freeze the extra, or skip the big pack because it would spoil
- Ingredient rules (Settings): never / cooked only / hidden / flavor only per ingredient, with "also counts as" names; recipes show what to change (leave out or swap), the menu planner avoids breaking them, left-out items stay off the shopping list, cooking steps remind about them
- Pregnancy guidance data starts empty and is filled in as recipes and ingredients are added (researched with Claude, approved by us); shown on the recipe and item pages, not on the shopping list
- Cooking mode: one step at a time, tappable timers, ingredients drawer, screen stays on, then update the pantry
- Data stays on the phone (IndexedDB), works offline once installed
- Backup: share/download a file, restore (merge or replace), erase all
- Installable on Android Chrome from a stable HTTPS address

## Definition of done
- [ ] Every v1 feature above works on the real target device (installed on my Android phone from the hosted address)
- [ ] "How to run" above is accurate, tested from scratch
- [ ] Tested by actually using it: planned a real week, built the list, shopped with it, marked meals cooked
- [ ] Backup -> erase -> restore tested on the phone, and a restore onto a second phone checked
- [ ] Hosted address recorded in `docs/hosting-and-install.md`
- [ ] Pushed to GitHub (private) with a clean `git status`
- [ ] Remaining ideas are parked under "Later", not half-built

## Later (parked ideas - do not build until v1 is done)
- Real APK via Capacitor + Android Studio (Play Store style install)
- Live sync between two phones (needs a Supabase or Firebase project)
- Barcode scanning to add pantry items
- Leftovers tracking, nutrition info, recipe photos
- Per-store aisle order for the shopping list
- Smarter ingredient matching and weight-to-volume conversions (cup of rice vs grams)
- Importing a recipe straight from a URL (needs a small proxy because of browser CORS limits)
- Servings stepper on the recipe page (today the household size in Settings scales everything)
- Rewriting recipe method text automatically when an ingredient is left out (today cooking mode shows a reminder instead)

## Changelog
- 2026-11-21: project created from `web-app` template
- 2026-11-21: v0.1 imported: PWA with on-device storage, TheMealDB search, paste import, backup/restore; tests passing in a desktop browser
- 2026-11-21: v0.2: warm homey redesign, bundled fonts, home dashboard, cooking mode, ingredient rules, shopping by store with buying advice, item sheet with pregnancy guidance (empty data) and ideas; backup format v2; tests extended
