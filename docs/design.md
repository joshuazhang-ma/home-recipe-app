# Design brief - Our Kitchen

Live design board (Claude artifact, all screens): https://claude.ai/artifact/4C6DzwsGENy1cTH1Aw8AtQ

## Direction
Warm and homey: like a well-loved family recipe box. Chosen over a first, louder "sticker" style.

## Tokens
| Token | Value | Use |
|-------|-------|-----|
| Linen | #FAF1E3 | page background |
| Cocoa | #3A2A1F | text, icons |
| Clay brown | #7A6354 | secondary text |
| Clay | #E7855B | main action, "need", "never" |
| Butter | #F4C86A | highlights, "partly", active tab |
| Sage | #A9C79A | "on hand", good |
| Duck egg | #9CC5C4 | time, timers, freeze/fits advice |
| Plum | #D2A8B8 | meal tags, traditional view |
| Apricot | #F5BE95 | food art, Costco |
Type: Fraunces (headings), Nunito (body), bundled in `src/fonts/`. Thin tan lines (1.5px #CDB594), soft shadows, rounded cards, pill buttons, 48px minimum touch targets (60px in cooking mode). Dark text on every coloured fill. Status is always a word as well as a colour. Dark mode follows the phone setting.

## Screens
Home dashboard, Menu, Recipes, Pantry, Shopping list (by store / by aisle), recipe sheet (pantry check, her rules, pregnancy check, ingredients, method), item sheet, ingredient rules (list and edit), cooking mode (step, ingredients drawer, finished / update pantry), settings. Bottom navigation: Home, Menu, Recipes, Pantry, Shop.

## Decisions from the design sessions
- Shopping list shows no pregnancy markers: guidance is for deciding what to buy, on the recipe and item pages.
- Pregnancy guidance data starts empty and is filled in later, item by item, with owner approval.
- Ingredient rules: see design-notes.md. Garlic cooked and hidden, onion never (incl. shallot, leek, chive), scallion flavor only and never as a garnish, onion/garlic powder never.
- Stores: Whole Foods, Costco, Trader Joe's, Wegmans, Wilson Farms, Elias Country Store, Other. Market Basket is deliberately not offered.
- Servings stepper on the recipe page was in the mock-up but is not built (household size in Settings scales recipes); parked under "Later".
