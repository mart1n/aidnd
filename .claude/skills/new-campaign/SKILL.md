---
name: new-campaign
description: Create a new AI&D campaign. Interviews the players about setting, tone, length, death rule and party (new heroes or saved ones), then writes the secret plot, the world map with towns and shops, and the starting state, and begins play. Use it when the players want to start a new game, adventure or campaign.
---

# /new-campaign

Make a new adventure with the players. This is fun, so keep the interview playful. Ask **one or two questions at a time**, offer examples, and make the kid's ideas matter.

## 1. Prepare

1. Run `python3 scripts/game.py sync`.
2. Run `python3 scripts/game.py list` to see existing characters and campaigns.
3. Read `rules/rules.md`, and the files in `templates/campaign/`. Those are the formats to follow.

## 2. Interview

Collect these, in roughly this order:

1. **Setting and vibe.**
   - Offer 3–4 quick pitches in one line each, plus "or invent your own". For example:
     - classic fantasy kingdom
     - sky islands and airships
     - haunted swamp
     - frozen north
     - desert of buried pyramids
     - underwater kingdom
   - Build on whatever they say. Ask for one or two things they really want in it, such as dragons, pirates, a talking cat or a volcano.
2. **Tone:**
   - silly and light
   - heroic adventure
   - mysterious and a bit spooky
   - a mix
3. **Length:**
   - **short:** about 3 sessions, 1 act
   - **medium:** about 6–10 sessions, 3 acts
   - **epic:** many sessions, 4–5 acts plus side quests
4. **Death rule.** Explain both simply, and recommend knockout for younger players.
   - **knockout (default):** heroes get knocked out and wake up in trouble.
   - **real:** heroes can truly die.
5. **The party:**
   - **How many heroes?** Usually one per player. A player may also run two.
   - **For each hero:** reuse a saved character from `list`, or make a new one.
   - **Reusing a hero:** a character with `activeCampaign` set to another active campaign must leave it first. Ask before moving them. In the old campaign, set their party entry's `status` to `away`.
   - **New heroes:** follow the `/new-character` skill for each one.
   - **Mixed levels** (for example a level 7 hero and a brand-new one): offer the new hero a **catch-up start** at the level of the lowest saved hero, minus 1 or 2. For each level gained, apply `/level-up` choices.
6. **Anything else?** Ask about favourite things, or things to avoid (for example "no spiders, please!"). Respect the "avoid" list strictly.

## 3. Build the campaign

Choose an `id`: a short, lowercase, dashed name, like `sky-pirates`. Create `campaigns/<id>/` with four files.

### campaign.md (secret)

Follow `templates/campaign/campaign.md`. Include:
- **Pitch**, **Setting** and **Tone.**
- **The secret story:** what's really going on, the villain (with a weakness), and the key NPCs.
- **Acts**, matching the chosen length. Each act has a goal and several ways to reach it.
- **Hooks and side quests:** at least 2, tied to places on the map.
- **Possible endings:** good, twisty and bad.
- **Planned treasure:** at least one exciting item per act, using `rules/items.md`. Pitch it at the party tier.
  - Plan one **legendary item** for the finale, with `growth` unlocks.
  - Include spell scrolls or teachers for spells the heroes would love, especially the spell casters.
- **Design for the party:** give each hero at least one moment to shine, using their class, backstory and spells.

### map.json

Follow `templates/campaign/map.json`.

**Size and shape:**
- **Regions:** 2–4, each with its own feel, for example forest, mountains, coast or badlands.
- **Locations:** 8–12 to start. They should include:
  - **at least 3 settlements:** at least 1 city and 1 town, with different services
  - **2–4 adventure sites:** dungeons, ruins, lairs
  - **1–3 landmarks**
- **Layout:** x/y from 0–100, with x running west → east and y running north → south. Spread places across the space, and keep labels apart: at least ~12 units between places.
- **Routes:** connect every place to at least one other. Each route needs a believable number of `days` (0.5–5), a `terrain`, and a `danger` from 0–5. Settlement-to-settlement roads should be safer than wild paths.

**What the players can see at the start:**
- The **starting town** is `discovered` and `visited`.
- **2–4 nearby or famous places** are `discovered`.
- **Everything else** is undiscovered, waiting for rumours and exploration.

**Settlements differ:**

| Kind | Services |
|---|---|
| Village | inn, maybe a general store |
| Town | inn, blacksmith, general store, maybe a temple |
| City | market, enchanter, `spell-academy:<element>`, temple, special shops |

**Each settlement's character:** at least one thing worth travelling for, like the frost academy, the dwarf forge or the beast market.

**Shops:**
- Only settlements the party can visit early need `shops` stock now. Others can be filled in on the first visit (see `/town`).
- **Stock size:** 4–8 items, pitched at the party tier and following `rules/items.md`.
- **Rarity:** mostly common or uncommon, with one rare item at tier 1 so there's something to save up for.
- Set each shop's `lastRestockDay` to 1.

**Inns:**
- Give each inn a name, a price (5 gold × tier) and 2–3 `rumours`.
- Rumours should point at undiscovered places and plot hooks from `campaign.md`.

**Secrets:** put what's really going on at each place in its `secret` field.

### state.json

Follow `templates/campaign/state.json`:
- **Basics:** `deathRule`, `status: "active"`, `tier` (from party level), `turn: 0`, `day: 1`, starting `location`.
- **Party:** one entry per hero, with full HP and mana (get the max values from `python3 scripts/game.py sheet <id>`), `status: "ok"`, empty `conditions` and `spent`, and `shortRests: 0`.
- **Quests:** the first quest, from act 1.
- **NPCs:** the NPCs the party meets first.
- `mapArtifactUrl: null`.

### log.md

Write the header, a "Story so far" section saying the adventure is just beginning, and an empty "Turns" list.

## 4. Link the heroes and save

1. Set each hero's `activeCampaign` to the new id in `characters/<id>.json`.
2. Remove any `_notes` fields copied from templates.
3. Run `python3 scripts/game.py check` and fix everything it reports.
4. Commit and push:
   `git add -A characters campaigns && git commit -m "[save] <id>: new campaign" && git push -u origin HEAD`

## 5. Begin

1. Present the campaign to the players: the title and a short, exciting pitch. **Never reveal secrets.**
2. Follow the `/map` skill to show the starting map.
3. Follow the `/play` skill from step 1.5 of "Starting a session": no recap, straight into the opening scene.
