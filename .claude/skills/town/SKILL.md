---
name: town
description: Run a visit to a town, city or village in an AI&D campaign. Covers shops with persistent stock (buy and sell), the inn (long rest and rumours that reveal map places), blacksmith, enchanter, spell academies and teachers, and temples. Use it when the party arrives in or explores a settlement, or wants to shop, rest at an inn, learn spells, or enchant gear.
---

# /town

Towns are where heroes spend gold, grow stronger and hear about new adventures. Make each one feel like a real place with its own character.

## 1. Arriving

1. Read the location in `campaigns/<id>/map.json`: its `description`, `notes`, `secret`, `services`, `inn` and `shops`. Also read the NPCs in `state.json` whose `location` is this place.
2. **First visit:**
   - Set `visited: true` (and `discovered: true`).
   - **If the town has no `shops` or `inn` yet,** create them now from its `services`, following section 3 of `/new-campaign` (shop stock and inns).
   - **Keep the services consistent with the town's size and character:** a village has no enchanter.
3. **Describe the town** in 3–5 lines: sights, sounds, one memorable local. Then list what's here, like a sign-post:
   *🍺 The Crooked Kettle (inn) · ⚒️ Dunmore's Anvil · 🛒 General store · ⛪ Temple of the Dawn*
4. **Ask where they go first.** The heroes can split up. Handle one visit at a time.

## 2. Shops

**Stock persists.** Shop stock lives in `map.json` → `shops.<shopId>.stock`. What players see there now is what's there next time, unless restocked.

**Restocking:** when the party enters a shop and `day − lastRestockDay ≥ 5`:
- Replace 1–2 items with new ones that fit the shop and the party's current tier.
- Sometimes add one exciting rare item.
- Set `lastRestockDay` to today.
- Mention it in the story: "Hilda's got something new from the mountain forges…"

**Showing stock:** show it as a short list with prices: `name (rarity): key properties, price g`. Comparing to what the hero has equipped helps.

**Buying:**
1. Check the gold.
2. Subtract the price from the buyer's `gold`.
3. Move the item from `stock` to the buyer's `backpack`, adding `slot` if missing.
4. Offer to equip it, following the `/sheet` skill.

**Haggling:** one Wits roll against Medium (12):
- **Success:** 10–20% off.
- **Natural 1:** the shopkeeper is offended. No sale today.
- Only once per shop per visit.

**Selling:** the shop pays **half the item's value**. Move the item from the hero's backpack into that shop's stock, at full value. It can be bought back later.

**Kinds of shop:**
- **Blacksmiths:** weapons and armor, and can turn a common weapon into a "fine" one for 50 gold: +1 to hit, recorded in `special`.
- **General stores:** potions, rope, tools, food.
- **Markets (cities):** a bit of everything, plus one curiosity stall.

## 3. The inn

**Long rest:**
- Costs the inn's `price` per hero, or is free if they make a friend of the innkeeper.
- Full HP and mana, `shortRests` = 0, `spent` = [], conditions cleared.
- Advance `day` by 1 and set `timeOfDay: "morning"`.

**Rumours:**
- Share 1–2 from the inn's `rumours`, or invent new ones that point at hooks in `campaign.md` and undiscovered places in `map.json`.
- **When a rumour names a place:** set it `discovered: true` in `map.json`, adding the place first if needed. Then offer to show the updated map with `/map`.
- **Use rumours up:** remove each one from the list once told, and add fresh ones as the story moves.

**Inns are social:** NPCs, bards, card games, quest-givers. A good place for a side quest.

## 4. Magic services

**Enchanter:**
- Follow "Enchanting" in `rules/items.md`: one new property per visit, priced by the new rarity, plus an ingredient for rare and above.
- Let the player choose the property from the rarity table.
- Update the item's fields, and set its `rarity` one step higher.

**Spell academy** (`spell-academy:<element>`):
- Teaches spells of that element, plus a few general Arcane spells.
- Prices are in rules section 5: Minor 50, Greater 300, Grand 1,500, Mythic 6,000.
- The hero must meet the circle's level. Learning takes a day: advance the day.
- No roll is needed. Add the spell at rank 1, mastery 0.
- Academies also sell scrolls, and may train ranks: +1 rank to a spell of their element for 100 × current rank gold, once per visit.

**Temple:**
- Healing: free for the kind, or a donation.
- Cures conditions and curses.
- Sells healing potions.
- In `real` death campaigns, a high priest can bring back a fallen hero, for a great price or a sacred quest.
- Temples may teach Radiant spells.

## 5. Leaving town

1. Check if they want anything else.
2. Ask where they're heading. Show route options from `map.json` with days, terrain and danger:
   `Frostspire: 3 days through the mountain pass (risky)`.
3. Hand back to the `/play` skill for travel.

## 6. Saving

After each purchase, sale, rest or other change:
1. Update the files.
2. Run `python3 scripts/game.py check <campaign>`.
3. Commit with `[save]` and push, as in `/play` section 6.
4. End replies with the footer from `python3 scripts/game.py footer <campaign>`.
