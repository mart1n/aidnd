---
name: invent-spell
description: Design a brand-new spell with a player. Turns their idea into a balanced spell (element, circle, mana cost, rank upgrades) and adds it to rules/spells.md, then decides how the hero gets it. Use it when a player wants to invent, create or make up a spell.
---

# /invent-spell

The player imagines a spell, and you help make it real and fair. This is where the kid gets to be a game designer. Say yes to the fun part of the idea, and balance the numbers quietly.

## Steps

1. **Read** `rules/rules.md` section 5 and a few spells in `rules/spells.md` of a similar kind, to match their power.
2. **Ask about the idea:**
   - **What does it do?**
   - **What does it look and sound like?**
   - **Which element** fits best? One of: Physical, Fire, Frost, Lightning, Poison, Shadow, Radiant, Arcane.
   - **Is it an attack, an area blast, a buff, a heal, or a trick or utility?**
3. **Balance it:**
   - **Circle:** pick it from how strong the effect is.
     - **Minor:** about 1d8 + Magic to one target, or a small trick.
     - **Greater:** about 3d6 to an area, or a strong condition.
     - **Grand:** battle-changing.
     - If the idea is too strong for the hero's level, make it a higher circle they can grow into, or give it a smaller Rank I that grows into the full idea at rank V or X. Kids love "it gets even cooler later".
   - **Mana cost:** in the circle's range.
   - **Rank I effect:** what it does when first learned.
   - **"Each rank":** the per-rank bonus.
   - **Unlocks:** new effects at ranks III and V, and maybe X.
4. **Name it** together, then show the finished spell card and adjust until the player loves it.
5. **Write it** into the `## Invented spells` section at the end of `rules/spells.md`, in exactly this format (the script reads the italic line):
   ```
   ### Spell Name
   *Element · Circle · N mana · Kind*
   One-line description. *Invented by <player> for <hero>.*
   - **Rank I:** …
   - **Each rank:** …
   - **Rank III:** …
   - **Rank V:** …
   ```
6. **How the hero gets it.** Let the player choose:
   - **Quest for it:** the DM hides a scroll, mentor or magical place with this spell in the current campaign. Note it under "DM notes during play" in `campaign.md`, and maybe add a rumour.
   - **Learn it at the next level-up,** as the "new spell" choice. The hero must meet the circle's level.
   - **Learn it now:** only if the story makes sense right now, and they're at a teacher, a rest with time to study, or similar.
7. **Validate and save:**
   - Run `python3 scripts/game.py check`.
   - Then: `git add -A rules characters campaigns && git commit -m "[save] new spell: <Spell Name>" && git push -u origin HEAD`
