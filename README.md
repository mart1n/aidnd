# AI&D

A light D&D-style adventure game where Claude is the Dungeon Master. It's built for a small party, such as a parent and child playing from a tablet with Claude Code.

- **Heroes live in `characters/`** and can join any campaign.
- **Campaigns live in `campaigns/`.** Each has its own world map with towns, shops and secrets.
- **Everything saves to git** after every turn.

## How to play

Open a Claude Code session on this repo (the iOS app works), then:

| Say | What happens |
|---|---|
| `/new-campaign` | build a new adventure and world map, choose or create heroes |
| `/play` (or "let's play") | continue the current adventure |
| `/sheet` | see a hero's stats, gear and spells, or change equipment |
| `/map` | see the world map |
| `/town` | shop, rest at the inn, learn spells, enchant gear |
| `/level-up` | level up (this usually happens automatically) |
| `/invent-spell` | design your own spell |
| `/new-character` | make a hero without starting a campaign |

## The game in one minute

- **Four stats:** Might, Agility, Wits and Magic.
- **Rolling:** roll d20 + stat, and beat the difficulty (8 easy → 16 hard → 24 legendary).
- **Classes:** Warrior, Rogue, Ranger, Mage and Cleric. Anyone can learn spells.
- **Spells are found in the world** and grow in rank as you use them. Mages and Clerics start with some.
- **Nine equipment slots**, and magic items that add stats, resistances, elemental damage and spell power.
- **No level cap.** The world scales up through threat tiers.
- **Each campaign chooses** "knocked out" or "real danger" for heroes who fall.

The full rules are in [`rules/rules.md`](rules/rules.md).

## For grown-ups

- **Where things are:** [`CLAUDE.md`](CLAUDE.md) explains the file layout and the save system. [`templates/`](templates/) has an annotated example of every file.
- **The helper script:** `python3 scripts/game.py --help` (dice, validation, sheets, map drawing).
- **Saves across sessions:** each Claude Code session may use its own branch. `/play` runs `game.py sync` first, which pulls in the newest `[save]` commit from any branch. Merging game branches into `main` from time to time keeps things tidy.
