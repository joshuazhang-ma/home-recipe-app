# CLAUDE.md - home-recipe-app

## Goal
A private Android app for our household ("Our Kitchen"): pantry, recipes, weekly menu, shopping list. Data lives on the phone; no accounts, no server.

## Stack
- Plain HTML/CSS/JavaScript, **no dependencies and no build step**. Single page: `src/index.html`. Fonts (Fraunces, Nunito) are bundled in `src/fonts/` and listed in `sw.js` so the app looks right offline.
- PWA: `src/sw.js` (offline cache), `src/manifest.webmanifest`, icons. Deployed by uploading the contents of `src/` to an HTTPS static host; installed from Android Chrome.
- Storage: IndexedDB database `ourkitchen`, object store `kv`, keys `collection/id` (collections: pantry, recipes, shopping, menu, settings, products, guidance, ideas). Products and guidance are keyed by the normalised ingredient name (`nameKey`); ingredient rules live in `settings/rules`. localStorage fallback only if IndexedDB is unavailable.
- Online recipes: TheMealDB free API (test key `1`). Everything else works offline.
- Tests: `tests/logic.test.js` (node) and `tests/pwa_test.py` (Playwright, search API mocked).

## Conventions
- Code in `src/`, tests in `tests/`, docs in `docs/`. Do not create new top-level folders without asking.
- File and folder names: kebab-case, no spaces.
- Secrets live only in `.env` (git-ignored). This app has none; keep it that way (no API keys in the client).
- Keep `README.md` current when behavior or run steps change.
- Make small, reviewable changes; commit with clear messages.
- Pure logic (parsing, matching, shopping maths, menu picking, ingredient rules, buying advice) stays between the `/*LOGIC_START*/` and `/*LOGIC_END*/` markers in `src/index.html` so `tests/logic.test.js` can load it. Keep it free of DOM access.
- Whenever anything in `src/` changes, bump `VERSION` in `src/sw.js`, or installed phones keep the old cached copy.
- Data shape changes must stay backward compatible with existing backups (`docs/design-notes.md` has the format), or include a migration.
- No new network calls beyond TheMealDB without asking (privacy is a feature).

## Do
- Ask before adding dependencies.
- Explain trade-offs briefly when there are several reasonable approaches.
- Run both tests before saying something works.
- Scope: build only what is listed under "v1 scope" in README.md. New ideas go to its "Later" list.

## Don't
- Don't modify anything outside this project folder.
- Don't delete files without asking.
- Don't add a backend, accounts or analytics.

## Current status / next steps
- v0.2 (Nov 2026): redesigned and extended per `docs/design.md`; logic and browser tests pass on desktop. Not yet hosted, not yet installed on the phone.
- Pregnancy guidance and best-product data are intentionally empty: fill them in with the owners as recipes and ingredients are added (propose, they approve). Never state medical guidance without a source.
- Next: host `src/`, install on the Android phone, then use it for one real week; log problems in `docs/` and fix only v1-scope issues.
