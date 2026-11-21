// Unit tests for the pure logic in src/index.html (code between the LOGIC_START / LOGIC_END markers).
// Run:  node tests/logic.test.js
const fs = require('fs'), path = require('path'), assert = require('assert');
const html = fs.readFileSync(path.join(__dirname, '..', 'src', 'index.html'), 'utf8');
const a = html.indexOf('/*LOGIC_START*/'), b = html.indexOf('/*LOGIC_END*/');
if (a < 0 || b < 0) throw new Error('logic markers not found in src/index.html');
const L = new Function(html.slice(a, b) +
  '\nreturn {parseIng,fmtIng,fmtQty,nameMatch,computeNeeds,toVirtual,pickRecipe,guessCat,defaultWeek,isoDate,DEFAULT_RULES,ruleFor,ruleHit,recipeRuleCheck,effRecipe,stepNotes,buyAdvice,useSoon,fmtClock,ruleDesc,timeMinutes,TIME_RE};')();

// ingredient line parsing
assert.deepStrictEqual(L.parseIng('2 cups flour'), { name: 'flour', qty: 2, unit: 'cup' });
assert.deepStrictEqual(L.parseIng('1 1/2 lb chicken thighs'), { name: 'chicken thighs', qty: 1.5, unit: 'lb' });
assert.deepStrictEqual(L.parseIng('200g rice'), { name: 'rice', qty: 200, unit: 'g' });
assert.deepStrictEqual(L.parseIng('½ tsp salt'), { name: 'salt', qty: .5, unit: 'tsp' });
assert.deepStrictEqual(L.parseIng('salt'), { name: 'salt', qty: 0, unit: '' });
assert.deepStrictEqual(L.parseIng('3 onions, diced'), { name: 'onions, diced', qty: 3, unit: '' });
assert.deepStrictEqual(L.parseIng('1 can (14 oz) diced tomatoes'), { name: '(14 oz) diced tomatoes', qty: 1, unit: 'can' });
assert.deepStrictEqual(L.parseIng('2-3 cloves garlic'), { name: 'garlic', qty: 2, unit: 'clove' });
assert.deepStrictEqual(L.parseIng('1 dozen eggs'), { name: 'eggs', qty: 1, unit: 'dozen' });
assert.deepStrictEqual(L.parseIng('2 tbsp of olive oil'), { name: 'olive oil', qty: 2, unit: 'tbsp' });
assert.strictEqual(L.fmtIng(L.parseIng('1 1/2 lb chicken')), '1½ lb chicken');

// name matching (every word of the recipe ingredient must appear in the pantry item's name)
assert(L.nameMatch('garlic cloves', 'garlic')); assert(L.nameMatch('onions, diced', 'yellow onion'));
assert(L.nameMatch('diced tomatoes', 'canned tomatoes')); assert(L.nameMatch('ground beef', 'beef mince'));
assert(!L.nameMatch('chicken broth', 'chicken breast'));

// shopping-list maths
const pantry = [{ id: '1', name: 'rice', qty: 500, unit: 'g' }, { id: '2', name: 'olive oil', qty: 1, unit: 'bottle', staple: true },
                { id: '3', name: 'onion', qty: 1, unit: '' }, { id: '4', name: 'flour', qty: 1, unit: 'cup' }];
const r1 = { id: 'a', servings: 2, ingredients: [{ name: 'rice', qty: 2, unit: 'cup' }, { name: 'onions', qty: 2, unit: '' }, { name: 'olive oil', qty: 2, unit: 'tbsp' }, { name: 'eggs', qty: 3, unit: '' }, { name: 'soy sauce', qty: 0, unit: '' }] };
const r2 = { id: 'b', servings: 2, ingredients: [{ name: 'flour', qty: 1.5, unit: 'cup' }, { name: 'eggs', qty: 2, unit: '' }] };
let needs = L.computeNeeds([{ recipe: r1, factor: 1 }, { recipe: r2, factor: 1 }], pantry);
const by = Object.fromEntries(needs.map(n => [n.name, n]));
assert.strictEqual(by['eggs'].qty, 5);          // summed across recipes
assert.strictEqual(by['onions'].qty, 1);        // 2 needed - 1 on hand
assert.strictEqual(by['flour'].qty, 0.5);       // 1.5 cup - 1 cup
assert(!by['olive oil']);                       // staple: never listed
assert(by['soy sauce'] && by['soy sauce'].qty === 0); // no-quantity item not in pantry
assert(!by['rice']);                            // cup vs g: dimension mismatch assumed covered (documented limit)
needs = L.computeNeeds([{ recipe: r2, factor: 2 }], []);
assert.strictEqual(needs.find(n => n.name === 'flour').qty, 3); // scaling
needs = L.computeNeeds([{ recipe: { ingredients: [{ name: 'chicken', qty: 1, unit: 'lb' }] }, factor: 1 }], [{ name: 'chicken breast', qty: 200, unit: 'g' }]);
assert.strictEqual(needs[0].unit, 'lb'); assert(Math.abs(needs[0].qty - 0.56) < 0.02);

// menu picking honours the avoid list and meal type
const recs = [r1, r2, { id: 'c', title: 'Peanut noodles', meals: ['dinner'], ingredients: [{ name: 'peanut butter', qty: 2, unit: 'tbsp' }] }];
const vp = L.toVirtual(pantry), used = new Set();
for (let i = 0; i < 3; i++) { const r = L.pickRecipe('dinner', recs, used, vp, () => 1, ['peanut'], new Date(), Math.random); assert(r && r.id !== 'c'); used.add(r.id); }
assert.strictEqual(L.pickRecipe('lunch', recs, used, vp, () => 1, [], new Date(), Math.random), null);

// categories and week logic
assert.strictEqual(L.guessCat('chicken thighs'), 'Meat & fish'); assert.strictEqual(L.guessCat('bell pepper'), 'Produce'); assert.strictEqual(L.guessCat('black pepper'), 'Spices & oils');
assert.strictEqual(L.isoDate(L.defaultWeek(new Date(2026, 10, 20))), '2026-11-23'); // Fri -> plan next week
assert.strictEqual(L.isoDate(L.defaultWeek(new Date(2026, 10, 18))), '2026-11-16'); // Wed -> this week
// ---- ingredient rules (her rules) ----
const R = L.DEFAULT_RULES, rf = n => (L.ruleFor(n, R) || {}).id;
assert.strictEqual(rf('2 cloves garlic'), 'garlic'); assert.strictEqual(rf('garlic cloves, minced'), 'garlic');
assert.strictEqual(rf('1 yellow onion'), 'onion'); assert.strictEqual(rf('shallots'), 'onion'); assert.strictEqual(rf('2 leeks'), 'onion'); assert.strictEqual(rf('chives'), 'onion');
assert.strictEqual(rf('scallions'), 'scallion'); assert.strictEqual(rf('green onions'), 'scallion'); assert.strictEqual(rf('spring onion'), 'scallion'); // more specific than onion
assert.strictEqual(rf('onion powder'), 'powders'); assert.strictEqual(rf('garlic powder'), 'powders'); // more specific than garlic / onion
assert.strictEqual(L.ruleFor('chicken thighs', R), null); assert.strictEqual(L.ruleFor('olive oil', R), null);
assert.strictEqual(L.ruleHit({ name: 'yellow onion' }, R).level, 'never');
assert.strictEqual(L.ruleHit({ name: 'onion soup mix' }, R).level, 'mild');       // prepared food: ok only if mild
assert.strictEqual(L.ruleHit({ name: 'scallions' }, R).level, 'note');
const bowl = { title: 'Bowl', ingredients: [{ name: 'yellow onion', qty: 1 }, { name: 'garlic', qty: 2, unit: 'clove' }, { name: 'scallions, for garnish', qty: 2 }, { name: 'rice', qty: 1, unit: 'cup' }],
  steps: ['Soften the onion.', 'Cook garlic gently.', 'Top with scallions to serve.'] };
const chk = L.recipeRuleCheck(bowl, R);
assert.strictEqual(chk.never.length, 1); assert.strictEqual(chk.notes.length, 2); assert.strictEqual(chk.garnish.length, 1); assert.strictEqual(chk.garnish[0].rule.id, 'scallion');
assert.strictEqual(L.recipeRuleCheck({ ingredients: [{ name: 'scallions', qty: 2 }], steps: ['Steam the fish with scallions.', 'Discard the scallions.'] }, R).garnish.length, 0); // flavor-only use is fine
// leaving out / swapping an ingredient
const adapted = L.effRecipe(Object.assign({}, bowl, { adapt: { leaveOut: ['yellow onion'], swaps: { 'garlic': 'ginger' } } }));
assert(!adapted.ingredients.some(g => /onion/.test(g.name))); assert(adapted.ingredients.some(g => g.name === 'ginger' && g.swappedFrom === 'garlic'));
assert.strictEqual(L.recipeRuleCheck(adapted, R).never.length, 0);
assert.strictEqual(L.effRecipe(bowl), bowl);
// the shopping list never asks for a left-out ingredient
assert(!L.computeNeeds([{ recipe: adapted, factor: 1 }], []).some(n => /onion/.test(n.name)));
// menu planner prefers recipes that follow her rules
const ok = { id: 'ok', title: 'Rice', meals: ['dinner'], ingredients: [{ name: 'rice', qty: 1, unit: 'cup' }] }, bad = { id: 'bad', title: 'Onion bowl', meals: ['dinner'], ingredients: [{ name: 'red onion', qty: 2 }, { name: 'rice', qty: 1, unit: 'cup' }] };
for (let i = 0; i < 20; i++) assert.strictEqual(L.pickRecipe('dinner', [bad, ok], new Set(), [], () => 1, [], new Date(), Math.random, R).id, 'ok');
assert.strictEqual(L.pickRecipe('dinner', [bad], new Set(), [], () => 1, [], new Date(), Math.random, R).id, 'bad'); // still plans when nothing else exists
// cooking-step reminders
const rs = (t, last) => L.stepNotes({ ingredients: [{ name: 'scallions' }, { name: 'garlic' }] }, t, last, R).map(n => n.text);
assert(rs('Steam the fish with scallions.', false).some(t => /Take out the scallion/.test(t)));
assert(rs('Add garlic and stir.', false).some(t => /^Garlic: cook it until the sharpness is gone/.test(t)));
assert(rs('Plate it up.', true).some(t => /Take out the scallion/.test(t))); assert.strictEqual(rs('Plate it up.', false).length, 0);
// buying advice (bulk or not)
const adv = (need, pack, keep, frz) => L.buyAdvice({ needV: need, packV: pack, shelfDays: keep, freezeOk: frz });
assert.strictEqual(adv(450, 454, 3, false).kind, 'fits');                 // 1 lb need, 1 lb pack
assert.strictEqual(adv(5, 16, 5, false).kind, 'skip');                    // spinach: 5 oz needed, 16 oz pack, keeps 5 days
assert.strictEqual(adv(5, 16, 5, true).kind, 'freeze');
assert.strictEqual(adv(454, 4540, 365, false).kind, 'bulk');              // rice: big bag keeps a year
assert.strictEqual(adv(450, 2700, 3, true).kind, 'freeze');               // chicken thighs 6 lb pack
assert.strictEqual(adv(2, 6, 0, false).kind, 'unknown'); assert.strictEqual(adv(2, 2, 0, false).packs, 1); assert.strictEqual(L.buyAdvice(null), null);
// use-it-up list and timers
const td = new Date(2026, 10, 21), up = L.useSoon([{ name: 'spinach', qty: 1, expires: '2026-11-23' }, { name: 'milk', qty: 1, expires: '2026-11-21' }, { name: 'rice', qty: 1, expires: '2027-01-01' }, { name: 'salt', staple: true, expires: '2026-11-22' }, { name: 'old', qty: 0, expires: '2026-11-20' }], td, 5);
assert.deepStrictEqual(up.map(p => p.name), ['milk', 'spinach']);
assert.strictEqual(L.fmtClock(360), '6:00'); assert.strictEqual(L.fmtClock(3725), '1:02:05'); assert.strictEqual(L.fmtClock(-4), '0:00');
const tm = new RegExp(L.TIME_RE.source, 'i').exec('Cook 5-7 minutes per side'); assert.strictEqual(L.timeMinutes(tm[0], tm[1], tm[2], tm[3]), 7);
assert(/Never|Not in the dish/.test(L.ruleDesc(R[1]))); assert(/mild/.test(L.ruleDesc(R[1])));
console.log('logic tests passed');
