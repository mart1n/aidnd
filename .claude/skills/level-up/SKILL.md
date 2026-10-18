---
name: level-up
description: Level up an AI&D character whose XP has reached 100 × level. Applies the reward choice, stat points every 4th level, and milestone titles and signature powers every 5th level, then saves. Use it during play when a hero earns enough XP, or when a player asks to level up.
---

# /level-up

Levelling up is a celebration. Make it feel big: a short dramatic moment in the story, then the choices.

## Steps

For each character whose `xp` is at least `100 × level`:

1. **Level up:**
   - Subtract `100 × level` from `xp`, then add 1 to `level`.
   - If XP is still enough for another level, repeat this skill afterwards.
2. **Show what grew automatically:**
   - Max HP and max mana grow by the class's `perLevel` values. Run `python3 scripts/game.py sheet <id>` to show the new numbers.
   - If they're in a campaign, refill their HP and mana to the new max in `state.json`. Levelling up is a full heal.
3. **The player chooses ONE reward** (rules section 7). Present the options with real examples from their own class list:
   - **New ability:**
     - Any ability from their class in `rules/classes.json` that they don't have yet and whose `level` is at most their new level.
     - **Or cross-training:** an ability from another class's list, with the same level rule.
     - Add it as `{ "id", "source", "name" }`, plus `choice` if needed.
   - **Spell rank:** +1 rank to a known spell. Reset its mastery to 0, and describe what the new rank does.
   - **New spell:**
     - Any spell of a circle they qualify for: Minor at level 1+, Greater at 5+, Grand at 10+, Mythic at 15+, Legendary at 20+.
     - Mages and Clerics pick freely. Other classes pick a spell they've seen in the world, or one from a related school.
     - Add it at rank 1, mastery 0.
   - **Toughen Up:** add +3 to both `boons.hp` and `boons.mana`.
4. **Every 4th level** (4, 8, 12…): also add +1 to one base stat in `stats`. The player chooses which.
5. **Every 5th level** (5, 10, 15…): a **milestone**.
   - **Title:** together with the player, pick a title for the `title` field, like "the Unseen".
   - **Signature power:**
     1. Use the class's `milestoneIdeas` for inspiration, and let the player dream big.
     2. Balance it: as strong as a Greater-circle spell at level 5, Grand at 10, Mythic at 15, and so on. It's usually once per rest or once per day.
     3. Add it to `abilities` with a custom `id` and `"source": "milestone"`, plus `name`, `uses` and `text`.
6. **Validate and save:**
   - Run `python3 scripts/game.py check`.
   - Then: `git add -A characters campaigns && git commit -m "[save] <Name> reached level <N>" && git push -u origin HEAD`
7. **Show the new sheet,** or just the changes, and get back to the story.
