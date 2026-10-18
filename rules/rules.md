# AI&D Rules

A light, D&D-style game for a small party, with an AI Dungeon Master (DM). Simple maths, lots of magic, gear to collect, and no level cap.

Numbers live in data files so scripts can use them:
- `rules/classes.json`: classes, starting kits, class abilities
- `rules/spells.md`: every spell in the world
- `rules/items.md`: weapons, armor, magic item rules, prices

---

## 1. Stats

Every character has four stats. Each one is a bonus you add to rolls.

| Stat | Used for |
|---|---|
| **Might** | melee attacks and damage, lifting, climbing, toughness. Adds to max HP. |
| **Agility** | ranged and light-weapon attacks, dodging, sneaking, locks, reflexes |
| **Wits** | noticing things, knowledge, puzzles, persuading, tricking, sensing lies |
| **Magic** | casting spells, learning spells, sensing and resisting magic. Adds to max mana. |

**At level 1:**
1. Put **+2, +1, +1, 0** into the four stats, in any order.
2. Add your class's **+1** to its key stat.

So a starting character has a best stat of +2 or +3.

**Stats grow slowly** (+1 every 4 levels), so the dice stay exciting forever. Most of your power comes from spells, abilities and gear.

The **effective stat** is the base stat plus every bonus from equipped items. Use the effective stat for all rolls.

---

## 2. The roll

When something is risky, roll **d20 + stat**, plus any item or spell bonus, and compare it with the difficulty:

| Difficulty | Target | Example |
|---|---|---|
| Easy | 8 | climb a knotted rope |
| Medium | 12 | pick a simple lock, calm a nervous horse |
| Hard | 16 | leap a chasm, fool a suspicious guard |
| Heroic | 20 | climb an icy cliff in a storm |
| Legendary | 24 | out-think an ancient dragon |
| Mythic | 28+ | bargain with a god |

- **Meets or beats the target:** success.
- **Natural 20** (the die shows 20): a great success with a bonus. In combat it is a **critical hit**: roll the damage dice twice.
- **Natural 1:** something goes wrong. In combat the attack misses, whatever the total.
- **Missed by 1 or 2:** **success at a cost**. You do it, but something else happens: you drop your torch, make noise, or take 1d4 damage. The story always keeps moving.
- **Advantage:** roll two d20s and keep the higher. Use it when the situation helps, for example an ally helps or you have the perfect tool.
- **Disadvantage:** roll two d20s and keep the lower. Use it when the situation hurts, for example you're blinded or it's pitch dark.
- **Helping:** a character who helps another gives them advantage, but shares the risk.

**Who rolls:** players roll for their own characters, including dodging attacks. Players can roll real dice and say the number, or ask the DM to roll for them with the dice script. The DM rolls for enemies and for hidden checks.

Only roll when failure would be interesting. Easy, safe things just happen.

---

## 3. Health, mana and rest

- **Max HP** = class base + class HP per level × (level − 1) + 2 × Might + item and boon bonuses.
- **Max mana** = class base + class mana per level × (level − 1) + 2 × Magic + item and boon bonuses.

`python3 scripts/game.py sheet <character>` calculates both.

**Resting:**
- **Short rest** (about an hour): regain half your max HP and half your max mana, rounded up. You get at most **2 short rests between long rests**.
- **Long rest** (a night's sleep at an inn or in a safe camp): regain everything and clear most conditions.
- **Abilities marked "once per rest"** come back after any rest.

**Healing potion:** restores 2d4 + 2 HP. Drinking one takes your action.

### When HP hits 0

Each campaign chooses one of two rules when it is created.

**Knockout rule (default):**
- At 0 HP you are **Down**. You can't act, but you're not dead.
- An ally can spend their action to heal you, or to pull you back up with a Medium (12) Wits or Magic check. You wake with 1 HP.
- After the fight, Down characters wake with 1 HP.
- **If the whole party is Down**, the battle is lost but the story goes on. You wake up captured, robbed, rescued by a stranger, or washed up somewhere strange. Losing should create a new adventure, not end one.

**Real danger rule:**
- At 0 HP you are **Dying**. At the start of each of your turns, roll a d20:
  - **10 or more:** a success.
  - **9 or less:** a failure.
  - **Natural 20:** you wake with 1 HP.
- **3 successes:** you stabilise and are Down.
- **3 failures:** the character **dies**.
- Any healing wakes a Dying character.
- A dead hero can only be brought back by rare and costly magic: a **Phoenix Draught** or **Scroll of Return** (see `rules/items.md`), a temple's high priest, a legendary item, or a quest to the land of the dead.
- When a character dies, set `status` to `dead` in the campaign's `state.json`. Leave the character file alone, so the hero is remembered.

---

## 4. Combat

**Turn order:**
1. Heroes act first, in any order they like.
2. Then all the enemies act.
3. Repeat.

If the party is **ambushed**, enemies go first in round 1. If the party **sneaks up** on enemies, the heroes get a free round first.

**On your turn:** move, plus **one action**. An action can be: attack, cast a spell, use an ability, drink a potion, help an ally, or try something creative. Creative ideas are encouraged; the DM picks a stat and a difficulty.

### Attacking

Roll **d20 + stat + item bonuses** against the enemy's **Defense**:
- **Melee weapons:** Might.
- **Ranged and light weapons:** Agility.
- **Attack spells:** Magic.

**On a hit,** roll the weapon's or spell's damage and add the same stat. For example, a longsword hit by a character with Might +2 deals 1d8 + 2.

### Defending

When an enemy attacks you, **you** roll to dodge: **d20 + Agility** against the enemy's **Attack** number.
- **Beat it:** you dodge, block or parry, and take no damage.
- **Fail:** you take the enemy's damage, reduced by your defenses.

**Area spells and traps** (fireballs, poison gas): roll d20 + Agility, or + Magic against magical effects. Success means half damage.

### Damage types

**Physical · Fire · Frost · Lightning · Poison · Shadow · Radiant · Arcane**

Every hit has a type. Weapons are physical unless they're magical. Arcane is pure magic, which almost nothing resists.

**Defenses, applied to each hit:**
- **Armor N:** reduces physical damage by N.
- **Resist [type] N:** reduces damage of that type by N.
- **Immune [type]:** that type does no damage at all. Very rare.
- **Vulnerable [type]:** that type does double damage, applied before reductions. Many monsters have a weakness, and finding it is part of the fun.
- **A hit that lands always does at least 1 damage,** unless the target is immune.

Armor and resistances from every equipped item add together.

### Conditions

| Condition | Effect |
|---|---|
| Burning | take 1d4 fire at the start of your turn, for 2 turns or until put out |
| Frozen | lose your next action, then thaw |
| Slowed | can't move far, and disadvantage on dodging |
| Poisoned | disadvantage on attacks until the end of the fight or until cured |
| Stunned | lose your next action |
| Frightened | disadvantage on everything while the source is in sight |
| Hidden | the next attack against an unaware target has advantage |
| Blessed | +1d4 to attack rolls and dodge rolls for the fight |
| Down / Dying | see section 3 |

---

## 5. Magic

**Anyone can learn spells.** Mages and Clerics are best at magic, but a Warrior who finds a scroll can learn it too.

### Spell circles

Every spell belongs to a **circle**. You must be at least the circle's level to learn its spells.

| Circle | Learn at level | Mana cost | Learning difficulty |
|---|---|---|---|
| Minor | 1 | 1–3 | 10 |
| Greater | 5 | 4–6 | 14 |
| Grand | 10 | 7–10 | 18 |
| Mythic | 15 | 11–15 | 22 |
| Legendary | 20 | 16+ | 26 |

### Learning a spell

Spells are found in the world:
- **Scroll:** during a rest, roll **d20 + Magic** against the learning difficulty.
  - **Success:** the scroll crumbles to dust and the spell is yours.
  - **Failure:** you keep the scroll, and can try again after your next level-up.
- **Teacher:** spell academies, hermits and temples teach spells for gold and a day of study. No roll is needed. Typical costs:
  - Minor: 50 gold
  - Greater: 300 gold
  - Grand: 1,500 gold
  - Mythic: 6,000 gold
- **Discovery:** a story event grants the spell, for example drinking from a starlit pool or a dying wizard's last gift. No roll is needed.
- **Level-up choice:** see section 7.

A character can know any number of spells.

### Casting

1. Pay the mana cost.
2. Attack spells roll d20 + Magic against the target's Defense. Other spells just happen, or the target rolls to resist.
3. Spell damage adds your Magic stat once per cast, the same way a weapon adds its stat.

### Spell ranks and mastery

Every known spell has a **rank**: I, II, III and so on, with **no limit**.
- **Earning mastery:** each time you cast a spell in a moment that matters (a fight, a puzzle, a dramatic scene), it gains **1 mastery**. Lighting a candle at dinner doesn't count.
- **Ranking up:** when mastery reaches **5 × the current rank**, the spell ranks up and mastery resets to 0. So rank I needs 5 casts, rank II needs 10, and so on.
- **What a rank gives:** each spell's entry lists what higher ranks add, usually more damage or duration. Most spells unlock a new effect at ranks III, V and X.
- **Spell Power:** some items add Spell Power for an element. A spell counts as that many ranks higher while the item is equipped. Its real rank and mastery don't change.

**Inventing spells:** use the `/invent-spell` skill. The DM balances the idea and adds it to `rules/spells.md`.

---

## 6. Equipment

Each character has nine slots:

| Slot | Holds |
|---|---|
| `head` | helmets, hats, circlets |
| `body` | armor, robes |
| `gloves` | gloves, gauntlets, bracers |
| `boots` | boots, shoes |
| `mainHand` | weapons, staves, wands |
| `offHand` | shields, a second light weapon, orbs, spellbooks, torches |
| `ring1`, `ring2` | rings |
| `neck` | amulets, necklaces, holy symbols |

- **Two-handed items** (greatswords, bows, big staves) go in `mainHand` and leave `offHand` empty.
- **Dual wielding:** two light weapons. The off-hand weapon can make one extra attack per turn, but it adds no stat to its damage.
- **The backpack** holds everything else, with no limit. Only equipped items give bonuses.
- **Changing gear** takes an action in combat. It's free outside combat.

Magic items, rarity, and what items can do are described in `rules/items.md`.

---

## 7. Progression

**XP:** each character needs **100 × current level** XP to reach the next level. XP resets to 0 on levelling up.

**Every level up:**
- Max HP and max mana grow automatically, from the class's per-level numbers.
- **Choose one reward:**
  - **Learn an ability:** from your class's list, or from another class's list (cross-training). Its level requirement still applies.
  - **Spell rank:** +1 rank to a spell you know.
  - **New spell:** learn a spell of a circle you qualify for. A Mage or Cleric picks freely; anyone else picks a spell they've seen in the world.
  - **Toughen up:** +3 max HP and +3 max mana permanently. This is recorded as a boon.
- **Every 4th level** (4, 8, 12, …): also gain **+1 to one stat**.
- **Every 5th level** (5, 10, 15, …): a **milestone**. Gain a **title** (for example *Kael the Unseen*) and a **signature power**, designed with the player and inspired by the class's milestone ideas. Signature powers are big and fun, usually once per rest or once per day.
- **Celebration:** levelling up restores full HP and mana.

**There is no level cap.** The world keeps up through threat tiers.

---

## 8. Threat tiers and enemies

**Party tier** = floor(average party level ÷ 5) + 1. So levels 1–4 are tier 1, levels 5–9 are tier 2, and so on. It never stops.

**A standard enemy of tier T:**

| | Formula | T1 | T2 | T3 | T4 | T5 |
|---|---|---|---|---|---|---|
| HP | 6 × T × (T + 1) | 12 | 36 | 72 | 120 | 180 |
| Defense (to hit it) | 9 + 2T | 11 | 13 | 15 | 17 | 19 |
| Attack (to dodge it) | 9 + 2T | 11 | 13 | 15 | 17 | 19 |
| Damage | T d6 + T | 1d6+1 | 2d6+2 | 3d6+3 | 4d6+4 | 5d6+5 |

**Variants:**
- **Minion:** 40% HP. Weak, comes in groups.
- **Brute:** +50% HP, −1 Defense.
- **Skirmisher:** +2 Defense, −25% HP.
- **Caster:** element damage, and maybe a condition.
- **Boss:** 4 × HP, 2 actions per round, one special move, and a weakness the party can discover.

Give enemies resistances and vulnerabilities that make sense: a fire elemental is immune to fire and vulnerable to frost.

**Pitching the danger:**
- **A fair fight:** about one standard enemy per hero.
- **Lower-tier enemies:** they should feel easy. That's the reward for growing strong.
- **Higher-tier enemies:** they are a warning to run, sneak or outsmart them.

---

## 9. Travel and exploration

Every campaign has a world map in `map.json`: places, regions, and routes with travel time in days, terrain and danger (1–5).

**Travel:**
- Move along routes between places.
- **Each travel day,** the DM rolls a d20. **On a result of danger × 3 or less, there is an encounter.** The encounter can be a fight, a strange traveller, a hidden place, or weather trouble.
- A **Ranger's Pathfinder** ability lets the party reroll one encounter check per journey.
- **Off-road exploring** reveals new places, which the DM adds to the map.

**Discovery:**
- **Rumours, maps and NPCs** reveal places ("heard of"). They appear on the party's map.
- **Visiting** a place marks it as visited.

---

## 10. Rewards

XP below is **per character, multiplied by the enemy's tier**:

| Event | XP |
|---|---|
| Easy encounter | 15 |
| Normal encounter | 40 |
| Hard encounter | 80 |
| Boss | 200 |
| Clever solution (avoiding a fight counts!) | the same as winning it |
| Quest step done | 50 |
| Quest complete | 150 |
| Great roleplay moment | 10–25 |

**Loot:** gold and items scale with tier. See `rules/items.md`. Not every fight drops magic items. **About 1 in 3 fights** should drop something interesting, and bosses always do.

---

## 11. Pets

Any hero can have pets. They're found, tamed, rescued, hatched or bought (beast markets in cities sell them).

- **Where they live:** in the character's `pets` list, so they follow the hero across campaigns: `{ "name", "kind", "trick", "hp", "notes" }`.
- **One trick each.** A pet has one helpful trick, used once per rest unless it says "always". For example: a raven fetches small things, a glimmerkit glows and sniffs out magic, a war hound bites (1d6 + tier physical). Using a trick is free; it doesn't take the hero's action.
- **In a fight,** enemies mostly ignore pets. A pet that is hit and drops to 0 HP **runs off and hides**, then comes back after the fight. **Pets never die**, even with the real danger rule.
- **Pets grow:** when its hero reaches a milestone level (5, 10, 15…), a pet can learn a second trick or grow into a bigger form. A dragon hatchling grows up slowly, one milestone at a time.
- **Taming a wild creature:** a Wits or Magic roll, harder for fiercer beasts, plus a good idea (food, kindness, a rescue).

---

## 12. Changing the rules

These rules are ours. When something isn't fun, change it here and note the change at the bottom.

### Rule changes
- v1: first version.
- v2: added pets (section 11), and revival items for the real danger rule (`rules/items.md`).
