# Items, Loot and Prices

## Item format

Items are JSON objects inside a character's `equipped` slots or `backpack`, or a shop's `stock`. Every field except `name` and `rarity` is optional:

```json
{
  "name": "Emberscale Armor",
  "rarity": "rare",
  "slot": "body",
  "armor": 2,
  "resist": { "fire": 3 },
  "stats": { "might": 1 },
  "hp": 5,
  "mana": 0,
  "damage": "1d8",
  "damageType": "physical",
  "extraDamage": [{ "dice": "1d4", "type": "fire" }],
  "spellPower": { "frost": 1 },
  "grantedSpells": [{ "spell": "light", "uses": "at will" }],
  "immune": ["poison"],
  "special": ["You can see in the dark"],
  "growth": [{ "level": 10, "unlock": "Resist fire becomes Immune fire" }],
  "twoHanded": false,
  "light": false,
  "ranged": false,
  "consumable": false,
  "value": 500,
  "lore": "Forged from the scales of the dragon Vorthax."
}
```

**`slot`** is one of `head`, `body`, `gloves`, `boots`, `hand`, `ring` or `neck`:
- **`hand`** items go in `mainHand` or `offHand`.
- **`ring`** items go in `ring1` or `ring2`.
- **No `slot`:** the item can't be worn, like a potion or a key. It lives in the backpack.

---

## Base weapons

| Weapon | Damage | Notes | Price |
|---|---|---|---|
| Dagger | 1d4 | light, can be thrown | 2 |
| Shortsword | 1d6 | light | 10 |
| Mace | 1d6 | | 5 |
| Spear | 1d6 | can be thrown | 3 |
| Longsword | 1d8 | | 15 |
| Battleaxe | 1d8 | | 12 |
| Warhammer | 1d8 | | 15 |
| Greatsword | 2d6 | two-handed | 50 |
| Greataxe | 1d12 | two-handed | 30 |
| Shortbow | 1d6 | two-handed, ranged | 25 |
| Longbow | 1d8 | two-handed, ranged | 50 |
| Crossbow | 1d10 | two-handed, ranged, reloads (no off-hand attack) | 60 |
| Staff | 1d6 | two-handed. Magic staves are where mages find power. | 5 |
| Wand | 1d4 arcane | ranged, uses Magic to hit. Useless as a club. | 40 |

**Which stat a weapon uses:**
- **Light and ranged weapons:** Agility.
- **Wands:** Magic.
- **Everything else:** Might.

## Base armor and off-hand items

| Item | Slot | Effect | Price |
|---|---|---|---|
| Robes | body | none, but some magic robes are the best mage gear | 5 |
| Leather Armor | body | Armor 1 | 10 |
| Chain Shirt | body | Armor 2 | 50 |
| Plate Armor | body | Armor 3, disadvantage on sneaking | 400 |
| Round Shield | hand | Armor 1 | 10 |
| Tower Shield | hand | Armor 2, can't be used with a two-handed weapon (no shield can) | 60 |
| Orb | hand | +2 mana (only magic orbs do more) | 50 |
| Torch | hand | light, 1d4 fire as a club | 1 |

Head, gloves, boots, rings and necklaces have no effect unless they are magic.

---

## Rarity

| Rarity | Properties | Shop price | Where found |
|---|---|---|---|
| Common | 0 (plain gear) | 1–50 | everywhere |
| Uncommon | 1 | 80–150 | most shops, normal loot |
| Rare | 2 | 400–800 | city shops, hard fights, bosses |
| Epic | 3 | 2,000–5,000 | rare merchants, bosses, deep dungeons |
| Legendary | 4 + growth | never sold | quests, great bosses, the story |

**What counts as a property** is one line of power:
- a stat bonus
- a resistance
- an extra-damage die
- Spell Power
- a granted spell
- an HP or mana bonus
- a special effect

A base weapon's damage or a base armor's Armor value doesn't count.

**Size of a property, by rarity:**

| Property | Uncommon | Rare | Epic | Legendary |
|---|---|---|---|---|
| Stat bonus | +1 | +1 | +2 | +2 or +3 |
| Resist [type] | 2 | 3 | 5 | 8, or Immune |
| Armor bonus (beyond the base) | +1 | +1 | +2 | +3 |
| Extra damage | 1d4 | 1d6 | 2d6 | 3d6 |
| Spell Power [element] | +1 | +1 | +2 | +3 |
| HP or mana bonus | +5 | +8 | +15 | +25 |
| Granted spell | Minor, once per rest | Minor at will, or Greater once per rest | Greater at will | Grand once per rest |

**Legendary items grow:** a legendary item has a `growth` list of new powers unlocked at character levels. They're designed around the story of the item, like a sword that wakes, a crown that remembers its old king, or armor made from a dragon.

**Matching loot to the party:** loot should be the party's tier or higher. At tier 1, a rare item is a big moment. At tier 3, rare items are normal and epic items are exciting.

## Consumables

| Item | Effect | Price |
|---|---|---|
| Healing Potion | 2d4+2 HP | 25 |
| Greater Healing Potion | 4d4+4 HP | 100 |
| Superior Healing Potion | 8d4+8 HP | 400 |
| Mana Potion | 2d4+2 mana | 30 |
| Greater Mana Potion | 4d4+4 mana | 120 |
| Antidote | ends Poisoned, Resist poison 5 for an hour | 20 |
| Smoke Bomb | everyone in an area becomes Hidden | 20 |
| Fire Flask | thrown: 2d6 fire, the target is Burning | 30 |
| Phoenix Draught (rare) | poured on a hero who died within the last hour: they return with half their max HP. Never sold in villages or towns | 600 |
| Scroll of Return (rare) | read aloud over a fallen hero, by anyone, within a day of their death: they return with 1 HP | 800 |
| Spell Scroll | learn the spell (see `rules/rules.md`, section 5) | Minor 60, Greater 350, Grand 1,800 |

## Gold

**Selling:** shops buy at half the item's value.

**Gold per normal fight, per tier:**

| Tier | Gold |
|---|---|
| 1 | 2d10 |
| 2 | 1d10 × 10 |
| 3 | 1d10 × 50 |
| 4 | 1d10 × 200 |

Bosses drop about 5 times as much.

## Enchanting

Enchanters, found in some cities, add **one property** to an item. That raises its rarity by one level: common becomes uncommon, uncommon becomes rare, and so on. Cost by the new rarity:

| New rarity | Gold | Plus |
|---|---|---|
| Uncommon | 100 | |
| Rare | 500 | a rare ingredient (dragon scale, phoenix feather, storm crystal…) |
| Epic | 3,000 | a legendary ingredient, usually earned on a quest |

Legendary items can't be enchanted. They grow on their own.

## Example magic items

These are for inspiration. Make new ones all the time.

| Item | Rarity | Slot | Properties |
|---|---|---|---|
| Boots of the Fox | uncommon | boots | Agility +1 |
| Gauntlets of Might | uncommon | gloves | Might +1 |
| Ring of Frost Ward | uncommon | ring | Resist frost 2 |
| Ring of Sparks | rare | ring | Magic +1, Spell Power lightning +1 |
| Helm of Clarity | uncommon | head | Wits +1 |
| Emberscale Armor | rare | body | Armor 2 (base), Resist fire 3, HP +8 |
| Flametongue Sword | rare | hand | 1d8 + 1d6 fire, sheds light |
| Staff of Frost | rare | hand, two-handed | 1d6, Spell Power frost +1, grants *Frost Ray* at will |
| Amulet of the Phoenix | epic | neck | Resist fire 5, HP +15, revive once per campaign at half HP |
| Cloak of Shadows (body) | rare | body | Armor 1, Agility +1, Resist shadow 3 |
| Thunderhammer | epic | hand, two-handed | 2d6 + 2d6 lightning, Might +2, Thunderclap once per rest |
| Wand of Light | uncommon | hand | grants *Light* at will |
| Orb of the Deep | rare | hand | mana +8, Spell Power frost +1 |
