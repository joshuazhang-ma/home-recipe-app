# Design notes - Our Kitchen

## Decisions
| Decision | Choice | Why / trade-off |
|----------|--------|-----------------|
| Platform | Installable web app (PWA) for Android Chrome | A native APK could not be built in Claude's workspace (Android SDK and Maven hosts blocked). A PWA installs from Chrome, works offline and needs no developer account. Capacitor APK is in README "Later". |
| Data location | On the phone only (IndexedDB), `navigator.storage.persist()` requested | Private, no accounts. Cost: data is per phone and per web address; clearing site data or uninstalling erases it. |
| Sharing with a second phone | Backup file, restore with Merge or Replace | Simple and private. Live sync would need Supabase/Firebase. |
| Menu planning | Rules, not AI | Offline, free, predictable. |
| Recipe discovery | TheMealDB search + paste-text import | Browsers cannot fetch arbitrary recipe URLs (CORS). TheMealDB allows it. |

## Menu planner
Each open slot gets the recipe with the best score among recipes tagged for that meal that avoid the avoid-list:
- pantry coverage (have = 1, have in a different unit = 0.8, partly = 0.5, missing = 0), x10
- +0.8 per ingredient (max 3) that is on hand and expires within 5 days
- +1 for favorites, -4 if cooked in the last 10 days, -1.5 if in the last 21
- a little randomness (top 3 weighted 1 / 0.5 / 0.25) so "Plan my week" gives variety
- earlier picks consume a simulated pantry so the week does not assume the same chicken twice
- no repeats until every eligible recipe has been used
On Fri-Sun the planner opens on next week. Locked and "eating out" slots are kept when re-planning.

## Shopping list
Ingredients of all planned meals (scaled to household size) are summed per ingredient and unit family (weight, volume, count/other), then the pantry is subtracted. Staples never appear. Items with no quantity ("salt") appear only if nothing matching is in the pantry. Auto items keep their checked state when the list is rebuilt; manual items are untouched.

## Known limits
- A recipe amount in volume (cup) against a pantry amount in weight (g) of the same ingredient is assumed covered.
- Matching is word based: every word of the recipe ingredient must appear in the pantry item's name ("oil" in the pantry does not cover "olive oil").
- TheMealDB quantities are for roughly 4 servings and sometimes vague ("1 large").
- No live sync; installing from a different web address starts with empty data (restore from a backup).

## Backup file format (JSON)
```
{ "app": "our-kitchen", "version": 2, "exported": "<ISO time>",
  "pantry":   { "<id>": { name, qty, unit, cat, expires, staple } },
  "recipes":  { "<id>": { title, servings, time, meals[], tags[], ingredients[{name,qty,unit}], steps[], notes, fav, lastCooked } },
  "shopping": { "<id>": { name, qty, unit, cat, auto, checked } },
  "menu":     { "<monday yyyy-mm-dd>": { week, slots: { "<dayIndex>-<meal>": { rid, locked } | { skip: true } } } },
  "settings": { "main": { servings, meals[], avoid[] }, "rules": { list: [{ id, name, usage[never|cooked|hidden|flavor], aliases[], prepared, swap, note }] } },
  "products": { "<nameKey>": { name, pick, store, price, packQty, packUnit, shelfDays, freezeOk } },
  "guidance": { "<nameKey>": { name, medical: { level[good|cook|limit|avoid], text, source }, traditional: { level[welcome|caution|avoid], text } } },
  "ideas":    { "<id>": { key, name, text, created } } }
```
A recipe may also carry `adapt: { leaveOut: [ingredient names], swaps: { "<ingredient name lower-case>": "<replacement>" } }`.
Restore accepts this shape (an `app` tag is not required). Version 1 backups still restore; the new collections are simply empty.
Guidance and product data can be prepared outside the app as a file in this format and merged with Settings > Restore from backup > Merge.

## Testing notes
- `tests/logic.test.js` loads the pure logic straight from `src/index.html`.
- `tests/pwa_test.py` checks: service worker active, manifest valid, data survives reload, app starts offline, online search (mocked) and offline message, paste import parsing, backup -> erase -> restore -> reload.
- `tests/pwa_test.py` also covers: her rules on a recipe (leave out), item sheet save, cooking mode with timer and drawer, shopping by store with buying advice, home dashboard, ingredient rules screen, fonts offline.
- Not yet tested: an actual Android phone (that is the Definition of done).

## Ingredient rules (her rules)
Per ingredient, one or more usages: **never** (overrides the rest), **cooked** (sharpness cooked out), **hidden** (not visible when served), **flavor** (used while cooking, removed before serving). Starting rules: garlic = cooked + hidden; onion = never (covers shallot, leek, chive; prepared sauces/stock ok only if mild); scallion = flavor only, never as a garnish; onion and garlic powder = never.
- The most specific alias wins ("green onion" is a scallion, not an onion; "garlic powder" is a powder, not garlic); on a tie the stricter rule wins.
- A recipe with a "never" ingredient shows a "Her rules" card: Leave it out, or Choose a swap. Both are stored on the recipe (`adapt`) and flow into the shopping list, pantry deduction, the menu planner and cooking mode.
- The planner prefers recipes without "never" ingredients; if none exist it still plans, and the slot shows the "Her rules" chip.
- "Flavor only" ingredients used as a garnish (ingredient line or step mentions garnish / sprinkle / top with / to serve) are flagged.
- Limit: method text is not rewritten. Cooking mode shows "You left out the onion. Skip it here." on steps that mention it.
- Limit: rules cannot see inside bought sauces or stock; the card tells you to check the label.

## Pregnancy guidance
Two tiers per ingredient: medical (FDA / ACOG style, shown as a firm label with a source) and traditional (shown softly as "gentle, not a rule"; the household follows it generally and has cheat days). The data starts empty. It is entered per ingredient in the item sheet (Edit details) or merged from a backup-format file prepared with Claude. Shown on the recipe page and the item sheet; deliberately not shown on the shopping list. Always general guidance, not medical advice; cite a source for the medical tier.

## Shopping advice
Each ingredient can have a preferred product, store, usual price, pack size, days it keeps and "freezes well". The shopping list groups by store and compares the needed amount with the pack size: one pack covers it (leftover <= 15%); otherwise the leftover is assumed to be used at the same weekly rate. If it keeps long enough: "Bulk ok"; if not and it freezes: "Freeze the extra"; if not: "Skip the big pack". With no keeping time entered, no bulk advice is shown. Pack and need must be in the same unit family (weight, volume or count).

## Cooking mode
Full-screen, one step at a time, with progress, tappable times that start a timer (one timer at a time, vibrates when done), an ingredients checklist drawer, reminders from the ingredient rules, and the screen kept awake where the browser allows it. Finishing opens the "update the pantry" sheet.
