---
name: new-character
description: Build a new AI&D hero step by step (name, class, stats, spells, gear, look and backstory) and save it to characters/. Use it when a player wants to make, create or roll up a new character or hero, or when /new-campaign needs one.
---

# /new-character

Guide one player through building a hero. Keep it quick and exciting, and explain choices in kid-friendly words. Ask one thing at a time, except where noted.

## 1. Prepare

1. Read `rules/rules.md` sections 1, 5 and 6, plus `rules/classes.json`.
2. Run `python3 scripts/game.py list` so you don't reuse an existing id.

## 2. Steps

1. **Who is playing?** Store the player's name in `player`.
2. **Class:**
   - Show each class from `classes.json`: its emoji, name and one-line `pitch`.
   - Mention that any hero can learn spells and can cross-train abilities from other classes later.
3. **Stats:**
   - Explain the four stats in one line each.
   - The player puts **+2, +1, +1, 0** wherever they like. Then add **+1 to the class's `keyStat`**.
   - Suggest a layout for the class, but let them choose.
4. **Spells:**
   - Add the class's `startingSpells.fixed` spells.
   - If `choose` is more than 0, let them pick that many from the `from` list. Show each spell's one-line description from `rules/spells.md`.
   - Every starting spell is rank 1 with mastery 0.
5. **Ability choices:** some starting abilities need a choice. For example, the Mage's Elemental Affinity needs an element. Store it as `"choice": "Fire"`. Suggest the element of their favourite starting spell.
6. **Gear:**
   - Give the class `kit`: put each slot's item in `equipped`, and the `backpack` list in the backpack.
   - Gold is the class's `startingGold`.
7. **Name, look, personality and backstory** (these can be asked together):
   - **Name.** Offer 3 ideas if they're stuck.
   - **One cool thing about how they look.**
   - **One personality trait.**
   - **One backstory hook:** "Where are you from, and what do you want?"
   - Fill in anything the player skips with something fun, and tell them what you added.
8. **Catch-up start** (only when `/new-campaign` asked for a higher level): set the level by applying one `/level-up` choice per level gained. The player picks each one quickly.

## 3. Write the file

Write `characters/<id>.json`, where the id is the name in lowercase with dashes. Follow `templates/character.json` exactly and leave out `_notes`. Fill in:
- `level: 1`, `xp: 0`, `title: null`
- `boons: { "hp": 0, "mana": 0, "armor": 0, "resist": {} }`
- **`abilities`:** objects with `id`, `source` (the class key) and `name`, plus `choice` if one was made.
- **`equipped`:** all 9 slots present, with `null` for empty slots.
- `activeCampaign: null`, unless `/new-campaign` is linking the hero.
- `history: []`

Then:
1. Run `python3 scripts/game.py check` and fix anything it reports.
2. Run `python3 scripts/game.py sheet <id>` and show the player their finished sheet. Make it a proud moment.
3. Save:
   `git add -A characters && git commit -m "[save] new hero: <Name>" && git push -u origin HEAD`

When called from `/new-campaign`, go back there afterwards.
