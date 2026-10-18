---
name: sheet
description: Show an AI&D character sheet (stats with gear bonuses, HP, mana, all 9 equipment slots, abilities, spells with ranks and mastery, backpack, legend), and equip, unequip or compare items. Use it when a player asks to see their character, stats, inventory, gear or spells, or wants to change equipment.
---

# /sheet

## Show a sheet

1. If no one is named, ask which hero. If there's only one, or the context makes it obvious, just show it.
2. Run `python3 scripts/game.py sheet <id>`. It shows current HP and mana from the active campaign.
3. Present the output as-is. It's already formatted. Add a short friendly line after it, such as:
   - "Firebolt is 2 casts away from rank III!"
   - "You have 85 gold. The Gauntlets of Might in Brindle cost 120."

## Equip, unequip or swap

**Outside combat it's free. In combat it costs the hero's action** (mention this, and let `/play` handle the turn).

1. **Slots:**
   - `head`, `body`, `gloves`, `boots`, `neck` take an item with that `slot`.
   - `mainHand` and `offHand` take items with `slot: "hand"`, or base weapons without a slot.
   - `ring1` and `ring2` take `slot: "ring"` items.
2. **Two-handed items** (`twoHanded: true`) go in `mainHand`, and anything in `offHand` moves to the backpack.
3. **Moving items:** move the old item to `backpack` and the new one into the slot. Never lose items.
4. **Comparing:** when asked, show what changes: run `sheet` before and after, or work it out from the item fields. For example: "Magic +1 → +2, Resist fire 0 → 3, max mana 8 → 10."
5. **Keep HP and mana within the new max:** if they're in an active campaign and max HP or max mana dropped, lower the current values in `state.json` to the new max.
6. **Validate and save:**
   - Run `python3 scripts/game.py check`.
   - Then: `git add -A characters campaigns && git commit -m "[save] <Name> changed gear" && git push -u origin HEAD`

## Other edits

- **Renaming, appearance, backstory:** fine anytime.
- **Stats, level, spells, gold:** only through play (`/play`, `/level-up`, `/town`). Don't hand-edit those just because someone asked, unless the players clearly agree it's a fix for a mistake.
