---
name: map
description: Show the AI&D campaign world map, meaning the places the party has discovered, routes with travel days and danger, and where they are now. Draws it as a web page that can be opened on a tablet. Use it when players ask for the map, where they are, where they can go, or after new places are discovered.
---

# /map

## Steps

1. **Pick the campaign.** It's usually the active one (`python3 scripts/game.py list`).
2. **Draw the map:** `python3 scripts/game.py map <campaign>` writes `campaigns/<campaign>/map.html`. The script only includes discovered places, and never includes `secret` fields, so the page is safe to show the players.
3. **Show it:**
   - **If the Artifact tool is available,** publish the page so it opens on the tablet. The page is already designed, so publish it as-is.
     - Follow the Artifact tool's own requirements. If it asks you to load a design skill first, do that, but don't restyle the generated page.
     - **First time (`state.json` → `mapArtifactUrl` is null):** publish `campaigns/<campaign>/map.html` with `icon: "map"` and a one-sentence description. Then store the returned URL in `mapArtifactUrl`.
     - **Later times:** update the same artifact by passing `url: <mapArtifactUrl>`. If the tool says you must read it first, do the `read`, then publish the regenerated file. That keeps one link that always shows the latest map.
   - **If the Artifact tool isn't available,** tell the players the map is in `campaigns/<campaign>/map.html` and can be opened from the session's files.
4. **Also give a short text version in chat,** for a quick glance:
   - where they are
   - the routes out of here, with days, terrain and danger
   - any places they've heard of but not visited
5. **Save:** run `python3 scripts/game.py check <campaign>`, then commit `map.html` (and `state.json` if the URL changed) with a `[save]` message, and push.

## Notes

- **The map grows as the story goes.** `/play` and `/town` add places and mark them discovered. Run this skill again after a discovery to update the picture.
- **Fixing an ugly map:** if two labels overlap, nudge the `x` and `y` of one place in `map.json` by a few units. Keep it believable: don't move places the players already know far away.
- **What the drawing shows:** visited places are solid symbols, and heard-of places are hollow. Route colours show danger: green is safe, amber is risky, red is dangerous.
