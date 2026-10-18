# Spell Book of the World

Every spell that exists. Characters list the spells they know in their file as `{ "id": "firebolt", "rank": 1, "mastery": 0 }`. The `id` is the spell name in lowercase with dashes, for example "Frost Ray" → `frost-ray`.

**Format, which `scripts/game.py` relies on:** a `### Spell Name` heading, then one italic line: `*Element · Circle · N mana · Kind*`.

**How ranks work:**
- A spell starts at rank I and grows with use: 5 × rank mastery to reach the next rank. See `rules/rules.md`, section 5.
- **"Each rank"** means the bonus is added for every rank above I.
- **"Your Magic"** means the caster's effective Magic stat.

**Kinds of spell:**
- **Attack:** roll d20 + Magic against Defense.
- **Area:** the targets roll to dodge for half damage.
- **Buff, Heal and Utility:** these just happen.

---

## Arcane

### Light
*Arcane · Minor · 1 mana · Utility*
A floating orb of soft light that follows you for an hour.
- **Rank I:** bright light around you, dim light beyond.
- **Rank III:** you can send the orb ahead to scout, up to a long hallway away, and see what it lights.
- **Rank V:** once per rest, flare it: every enemy who sees it must dodge or be blinded (disadvantage) for a round.

### Arcane Missile
*Arcane · Minor · 2 mana · Attack*
Three darts of violet force that never miss.
- **Rank I:** automatically hits for 1d4 + your Magic arcane (no roll needed). You can split the darts between targets: each dart does 1d4, and the Magic bonus goes to the first dart only.
- **Each rank:** +1 dart (1d4).
- **Rank V:** the darts pierce Arcane resistance.

### Mage Hand
*Arcane · Minor · 1 mana · Utility*
A ghostly hand that lifts, pulls and fiddles things at a distance.
- **Rank I:** lift something as heavy as a cat, open doors, pull levers.
- **Rank III:** the hand can pick locks with your Agility, and use thieves' tools.
- **Rank V:** the hand can grab an enemy's weapon (Magic against their Defense) and yank it away.

### Detect Magic
*Arcane · Minor · 1 mana · Utility*
For a few minutes, magic glows to your eyes.
- **Rank I:** see auras on magic items, spells and enchanted creatures nearby.
- **Rank III:** know the element and rarity of what you see.
- **Rank V:** see through magical disguises and invisibility.

### Arcane Shield
*Arcane · Greater · 4 mana · Buff*
A shimmering barrier springs up when you need it, even on an enemy's turn.
- **Rank I:** react to being attacked: +5 to your dodge roll against that attack.
- **Each rank:** +1 to the bonus.
- **Rank III:** you can protect an ally instead.

---

## Fire

### Firebolt
*Fire · Minor · 2 mana · Attack*
A streak of flame hurled from your hand.
- **Rank I:** hit for 1d8 + your Magic fire.
- **Each rank:** +1d4 damage.
- **Rank III:** the target is Burning.
- **Rank V:** the bolt splits to hit a second target. Roll separately.
- **Rank X:** the bolt explodes, hitting everything near the target.

### Fire Shield
*Fire · Greater · 5 mana · Buff*
Flames wrap your body without burning you.
- **Rank I:** for the fight, gain Resist frost 3, and anyone who hits you in melee takes 1d6 fire.
- **Each rank:** +1 resist, +1 fire damage.
- **Rank V:** you can give the shield to an ally instead.

### Fireball
*Fire · Greater · 6 mana · Area*
A bead of fire that blooms into a roaring explosion.
- **Rank I:** everything in a room-sized area must dodge or take 3d6 + your Magic fire. A dodge halves it.
- **Each rank:** +1d6 damage.
- **Rank III:** you can shape it so allies inside are not hurt.
- **Rank V:** everything hit is Burning.

### Meteor
*Fire · Grand · 9 mana · Area*
Call a burning stone from the sky.
- **Rank I:** a huge area takes 6d6 + your Magic fire plus 2d6 physical. A dodge halves it. It takes one round to arrive.
- **Each rank:** +1d6 fire.
- **Rank III:** call two meteors at once.

---

## Frost

### Frost Ray
*Frost · Minor · 2 mana · Attack*
A beam of numbing cold.
- **Rank I:** hit for 1d6 + your Magic frost, and the target is Slowed.
- **Each rank:** +1d4 damage.
- **Rank III:** on a natural 18–20, the target is Frozen.
- **Rank V:** the ray passes through to hit a second target behind the first.

### Ice Armor
*Frost · Minor · 3 mana · Buff*
A coat of hard frost covers you.
- **Rank I:** for the fight, gain Armor +2 and Resist fire 2.
- **Each rank:** +1 Armor.
- **Rank III:** anyone who hits you in melee is Slowed.
- **Rank V:** you can cast it on an ally.

### Freeze
*Frost · Greater · 5 mana · Attack*
Encase a foe in ice.
- **Rank I:** on a hit, the target is Frozen and takes 2d6 frost.
- **Each rank:** +1d6 damage.
- **Rank III:** you can freeze water solid: a bridge across a river, or a wall of ice.
- **Rank V:** the target stays Frozen for 2 turns.

### Blizzard
*Frost · Grand · 8 mana · Area*
A howling storm of ice and wind.
- **Rank I:** for 3 rounds, enemies in a large area take 2d6 + your Magic frost each round and are Slowed. A dodge halves it.
- **Each rank:** +1d6 damage.
- **Rank V:** allies inside are hidden by the snow.

---

## Lightning

### Spark
*Lightning · Minor · 2 mana · Attack*
A crackling bolt that jumps between foes.
- **Rank I:** hit for 1d8 + your Magic lightning. On a hit it jumps to a second target for 1d4.
- **Each rank:** +1d4 to the first target.
- **Rank III:** it jumps to a third target.
- **Rank V:** targets wearing metal armor are Stunned.

### Thunderclap
*Lightning · Minor · 3 mana · Area*
A deafening boom around you.
- **Rank I:** everyone next to you must dodge or take 1d8 lightning and be pushed back. A dodge halves the damage and means no push.
- **Each rank:** +1d4 damage.
- **Rank III:** anyone pushed is also Stunned.

### Chain Lightning
*Lightning · Greater · 6 mana · Attack*
A storm-bolt that leaps from enemy to enemy.
- **Rank I:** hit up to 4 targets (roll for each) for 2d8 + your Magic lightning.
- **Each rank:** +1 target.
- **Rank V:** the lightning never jumps to allies, and does +1d8 damage.

### Storm Call
*Lightning · Grand · 9 mana · Area*
Summon a thundercloud that obeys you.
- **Rank I:** for the fight, once per round as a free action, strike one enemy for 3d8 lightning (Attack roll).
- **Each rank:** +1d8 damage.
- **Rank V:** strike two enemies each round.

---

## Poison

### Poison Spray
*Poison · Minor · 2 mana · Attack*
A cloud of green venom from your palm.
- **Rank I:** hit for 1d10 + your Magic poison.
- **Each rank:** +1d4 damage.
- **Rank III:** the target is Poisoned.
- **Rank V:** it hits a cone: up to 3 targets next to each other.

### Toxic Cloud
*Poison · Greater · 5 mana · Area*
A lingering yellow-green fog.
- **Rank I:** a room-sized cloud lasts 3 rounds. Anyone starting their turn in it takes 2d6 poison and is Poisoned. A dodge halves the damage and avoids Poisoned.
- **Each rank:** +1d6 damage.
- **Rank III:** you can move the cloud each round.

---

## Shadow

### Shadow Step
*Shadow · Minor · 2 mana · Utility*
Melt into one shadow and step out of another.
- **Rank I:** teleport to a shadow you can see, up to about 30 paces.
- **Rank III:** take one ally with you.
- **Rank V:** you arrive Hidden.

### Frighten
*Shadow · Minor · 2 mana · Attack*
Show an enemy its worst fear.
- **Rank I:** on a hit, the target is Frightened for the fight and takes 1d6 shadow.
- **Each rank:** +1d4 damage.
- **Rank III:** a Frightened minion flees.

### Darkness
*Shadow · Minor · 2 mana · Utility*
A sphere of magical darkness.
- **Rank I:** a room-sized area becomes pitch black for a minute. Normal light can't pierce it.
- **Rank III:** you and your allies can see inside it.
- **Rank V:** enemies inside take 1d6 shadow each round.

### Shadow Bolt
*Shadow · Greater · 4 mana · Attack*
A bolt of living darkness.
- **Rank I:** hit for 3d6 + your Magic shadow. You heal half the damage dealt.
- **Each rank:** +1d6 damage.
- **Rank V:** the target is Frightened.

---

## Radiant

### Heal
*Radiant · Minor · 2 mana · Heal*
Warm golden light closes wounds.
- **Rank I:** touch: heal 1d8 + your Magic.
- **Each rank:** +1d4 healing.
- **Rank III:** works at range.
- **Rank V:** also ends Poisoned or Burning.

### Sacred Flame
*Radiant · Minor · 2 mana · Attack*
A pillar of holy fire falls on an enemy.
- **Rank I:** hit for 1d8 + your Magic radiant. Undead and shadow creatures take +1d8.
- **Each rank:** +1d4 damage.
- **Rank III:** the target can't become Hidden or invisible for the fight.

### Bless
*Radiant · Minor · 2 mana · Buff*
A prayer that guides your allies' hands.
- **Rank I:** up to 3 allies are Blessed for the fight.
- **Rank III:** Blessed allies also gain Resist shadow 2.
- **Rank V:** Blessed adds 1d6 instead of 1d4.

### Healing Wave
*Radiant · Greater · 5 mana · Heal*
Light washes over the whole party.
- **Rank I:** every ally nearby heals 2d6 + your Magic.
- **Each rank:** +1d6 healing.
- **Rank V:** enemies of shadow or undeath in the wave take the same amount as radiant damage.

### Sunburst
*Radiant · Grand · 8 mana · Area*
The light of noon, all at once.
- **Rank I:** every enemy in a large area takes 5d6 radiant and is blinded (disadvantage) for a round. A dodge halves it and avoids the blinding. Undead take double.
- **Each rank:** +1d6 damage.

---

## Nature

### Entangle
*Physical · Minor · 2 mana · Area*
Vines and roots burst from the ground.
- **Rank I:** enemies in an area must dodge or be Slowed and unable to move for a round.
- **Rank III:** trapped enemies take 1d6 physical each round.
- **Rank V:** the vines last until destroyed.

### Thorn Whip
*Physical · Minor · 2 mana · Attack*
A whip of thorny vine that lashes and pulls.
- **Rank I:** hit for 1d6 + your Magic physical, and pull the target toward you.
- **Each rank:** +1d4 damage.
- **Rank III:** the target is Poisoned by the thorns.

### Speak with Animals
*Arcane · Minor · 1 mana · Utility*
For an hour, you understand and can talk to animals.
- **Rank I:** talk with animals. They're as clever as animals are.
- **Rank III:** ask an animal for a small favour: scout, fetch, distract.
- **Rank V:** talk to plants too. Trees remember a lot.

### Barkskin
*Physical · Greater · 4 mana · Buff*
Skin as hard as old oak.
- **Rank I:** for the fight, an ally gains Armor +3.
- **Each rank:** +1 Armor.
- **Rank III:** also Resist poison 3.

---

## Invented spells

Spells created with `/invent-spell` go here. Each entry notes who invented it.
