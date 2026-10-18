#!/usr/bin/env python3
"""AI&D helper: dice, validation, character sheets, the turn footer, map drawing and save syncing.

Usage:
  python3 scripts/game.py roll d20+3 [2d6+1 ...] [--adv|--dis] [--label TEXT]
  python3 scripts/game.py list
  python3 scripts/game.py check [CAMPAIGN]
  python3 scripts/game.py sheet CHARACTER [--campaign CAMPAIGN]
  python3 scripts/game.py footer CAMPAIGN
  python3 scripts/game.py map CAMPAIGN [-o OUTPUT.html]
  python3 scripts/game.py sync

Standard library only.
"""

import argparse
import html
import json
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARACTERS = ROOT / "characters"
CAMPAIGNS = ROOT / "campaigns"
RULES = ROOT / "rules"

STATS = ["might", "agility", "wits", "magic"]
STAT_SHORT = {"might": "Mi", "agility": "Ag", "wits": "Wi", "magic": "Ma"}
SLOTS = ["head", "body", "gloves", "boots", "mainHand", "offHand", "ring1", "ring2", "neck"]
SLOT_KIND = {"mainHand": "hand", "offHand": "hand", "ring1": "ring", "ring2": "ring"}
DAMAGE_TYPES = ["physical", "fire", "frost", "lightning", "poison", "shadow", "radiant", "arcane"]
RARITIES = ["common", "uncommon", "rare", "epic", "legendary"]
LOCATION_TYPES = ["city", "town", "village", "dungeon", "ruin", "landmark", "camp", "wild"]
STATUSES = ["ok", "down", "dying", "dead", "away"]
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


# ---------- loading ----------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_classes():
    return {k: v for k, v in load_json(RULES / "classes.json").items() if not k.startswith("_")}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower().replace("'", "")).strip("-")


def load_spells():
    """Parse rules/spells.md into {id: {name, element, circle, cost, kind}}."""
    spells = {}
    lines = (RULES / "spells.md").read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("### "):
            continue
        name = line[4:].strip()
        meta = {"name": name, "element": "?", "circle": "?", "cost": 0, "kind": "?"}
        for nxt in lines[i + 1:i + 4]:
            m = re.match(r"^\*(.+?)\s*·\s*(.+?)\s*·\s*(\d+)\s*mana\s*·\s*(.+?)\*\s*$", nxt.strip())
            if m:
                meta.update(element=m.group(1), circle=m.group(2), cost=int(m.group(3)), kind=m.group(4))
                break
        spells[slugify(name)] = meta
    return spells


def character_path(cid):
    return CHARACTERS / f"{cid}.json"


def load_character(cid):
    return load_json(character_path(cid))


def campaign_dir(cid):
    return CAMPAIGNS / cid


def load_campaign(cid):
    d = campaign_dir(cid)
    return load_json(d / "state.json"), load_json(d / "map.json")


def roman(n):
    return ROMAN[n] if 0 <= n < len(ROMAN) else str(n)


# ---------- derived numbers ----------

def equipped_items(ch):
    return [it for it in (ch.get("equipped") or {}).values() if isinstance(it, dict)]


def derived(ch, classes):
    """Effective stats, max HP/mana, armor, resistances, spell power, from base + equipped items + boons."""
    cls = classes.get(ch.get("class"), {})
    items = equipped_items(ch)
    eff = {s: int((ch.get("stats") or {}).get(s, 0)) for s in STATS}
    hp_bonus = int((ch.get("boons") or {}).get("hp", 0))
    mana_bonus = int((ch.get("boons") or {}).get("mana", 0))
    armor = int((ch.get("boons") or {}).get("armor", 0))
    resist, power, immune = {}, {}, set()
    for it in items:
        for s, v in (it.get("stats") or {}).items():
            eff[s] = eff.get(s, 0) + int(v)
        hp_bonus += int(it.get("hp", 0))
        mana_bonus += int(it.get("mana", 0))
        armor += int(it.get("armor", 0))
        for t, v in (it.get("resist") or {}).items():
            resist[t] = resist.get(t, 0) + int(v)
        for t, v in (it.get("spellPower") or {}).items():
            power[t] = power.get(t, 0) + int(v)
        immune.update(it.get("immune") or [])
    for t, v in ((ch.get("boons") or {}).get("resist") or {}).items():
        resist[t] = resist.get(t, 0) + int(v)
    if any(a.get("id") == "iron-skin" for a in ch.get("abilities", [])):
        armor += 1
    level = int(ch.get("level", 1))
    hp = cls.get("hp", {"base": 10, "perLevel": 4})
    mana = cls.get("mana", {"base": 4, "perLevel": 2})
    max_hp = hp["base"] + hp["perLevel"] * (level - 1) + 2 * eff["might"] + hp_bonus
    max_mana = mana["base"] + mana["perLevel"] * (level - 1) + 2 * eff["magic"] + mana_bonus
    return {
        "stats": eff, "maxHp": max(1, max_hp), "maxMana": max(0, max_mana),
        "armor": armor, "resist": resist, "spellPower": power, "immune": sorted(immune),
        "xpNext": 100 * level, "tier": level // 5 + 1,
    }


def signed(n):
    return f"+{n}" if n >= 0 else str(n)


# ---------- dice ----------

DICE_RE = re.compile(r"^(\d*)d(\d+)((?:[+-]\d+)*)$")


def roll_expr(expr, adv=False, dis=False):
    expr = expr.replace(" ", "").lower()
    m = DICE_RE.match(expr)
    if not m:
        try:
            return f"{expr} → {int(expr)}", int(expr), None
        except ValueError:
            raise SystemExit(f"Can't read dice '{expr}'. Use forms like d20+3, 2d6, 1d8-1.")
    n = int(m.group(1) or 1)
    sides = int(m.group(2))
    mod = sum(int(x) for x in re.findall(r"[+-]\d+", m.group(3) or ""))
    if (adv or dis) and n == 1:
        a, b = random.randint(1, sides), random.randint(1, sides)
        kept = max(a, b) if adv else min(a, b)
        rolls_txt = f"[{a}, {b}] keep {kept}"
        rolls = [kept]
    else:
        rolls = [random.randint(1, sides) for _ in range(n)]
        rolls_txt = "[" + ", ".join(map(str, rolls)) + "]"
    total = sum(rolls) + mod
    mod_txt = f" {'+' if mod >= 0 else '-'} {abs(mod)}" if mod else ""
    nat = rolls[0] if n == 1 and sides == 20 else None
    flag = ""
    if nat == 20:
        flag = "  ★ NATURAL 20!"
    elif nat == 1:
        flag = "  ✖ natural 1"
    return f"{expr} → {rolls_txt}{mod_txt} = {total}{flag}", total, nat


def cmd_roll(args):
    if args.label:
        print(f"🎲 {args.label}")
    indent = "   " if args.label else ""
    for e in args.dice:
        print(indent + roll_expr(e, args.adv, args.dis)[0])


# ---------- validation ----------

def check_item(item, where, errors, slot=None):
    if not isinstance(item, dict):
        errors.append(f"{where}: item must be an object")
        return
    if not item.get("name"):
        errors.append(f"{where}: item has no name")
    if item.get("rarity") not in RARITIES:
        errors.append(f"{where}: rarity '{item.get('rarity')}' should be one of {RARITIES}")
    for t in list((item.get("resist") or {}).keys()) + list((item.get("spellPower") or {}).keys()) + list(item.get("immune") or []):
        if t not in DAMAGE_TYPES:
            errors.append(f"{where}: unknown damage type '{t}'")
    if item.get("damageType") and item["damageType"] not in DAMAGE_TYPES:
        errors.append(f"{where}: unknown damageType '{item['damageType']}'")
    for s in (item.get("stats") or {}):
        if s not in STATS:
            errors.append(f"{where}: unknown stat '{s}'")
    if slot:
        want = SLOT_KIND.get(slot, slot)
        has = item.get("slot")
        if has and has != want:
            errors.append(f"{where}: a '{has}' item can't go in the {slot} slot")


def check_character(cid, ch, classes, spells, errors):
    w = f"characters/{cid}.json"
    if ch.get("id") != cid:
        errors.append(f"{w}: id '{ch.get('id')}' should match the file name '{cid}'")
    if ch.get("class") not in classes:
        errors.append(f"{w}: class '{ch.get('class')}' isn't in rules/classes.json")
    for s in STATS:
        if not isinstance((ch.get("stats") or {}).get(s), int):
            errors.append(f"{w}: stats.{s} missing or not a whole number")
    level = ch.get("level")
    if not isinstance(level, int) or level < 1:
        errors.append(f"{w}: level must be 1 or more")
        level = 1
    if ch.get("xp", 0) < 0:
        errors.append(f"{w}: xp can't be negative")
    elif ch.get("xp", 0) >= 100 * level:
        errors.append(f"{w}: xp {ch.get('xp')} has reached {100 * level}. Time to level up (use /level-up)")
    eq = ch.get("equipped") or {}
    for k in eq:
        if k not in SLOTS:
            errors.append(f"{w}: '{k}' isn't a slot. Slots are {SLOTS}")
    for slot in SLOTS:
        if eq.get(slot) is not None:
            check_item(eq[slot], f"{w} equipped.{slot}", errors, slot)
    main = eq.get("mainHand")
    if isinstance(main, dict) and main.get("twoHanded") and eq.get("offHand"):
        errors.append(f"{w}: {main.get('name')} is two-handed, so offHand must be empty")
    for i, it in enumerate(ch.get("backpack") or []):
        check_item(it, f"{w} backpack[{i}]", errors)
    for i, sp in enumerate(ch.get("spells") or []):
        if sp.get("id") not in spells:
            errors.append(f"{w}: spell '{sp.get('id')}' isn't in rules/spells.md")
        rank = sp.get("rank", 1)
        if not isinstance(rank, int) or rank < 1:
            errors.append(f"{w}: spell '{sp.get('id')}' needs a rank of 1 or more")
        elif sp.get("mastery", 0) >= 5 * rank:
            errors.append(f"{w}: spell '{sp.get('id')}' has {sp.get('mastery')} mastery, so it should rank up to {roman(rank + 1)}")
    if not isinstance(ch.get("gold", 0), int) or ch.get("gold", 0) < 0:
        errors.append(f"{w}: gold must be a whole number, 0 or more")
    ac = ch.get("activeCampaign")
    if ac and not (campaign_dir(ac) / "state.json").exists():
        errors.append(f"{w}: activeCampaign '{ac}' doesn't exist")


def check_campaign(cid, classes, errors):
    w = f"campaigns/{cid}"
    d = campaign_dir(cid)
    for f in ["state.json", "map.json", "campaign.md", "log.md"]:
        if not (d / f).exists():
            errors.append(f"{w}: missing {f}")
    if errors and not (d / "state.json").exists():
        return
    try:
        state, world = load_campaign(cid)
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{w}: can't read state.json/map.json: {e}")
        return
    if state.get("deathRule") not in ("knockout", "real"):
        errors.append(f"{w}/state.json: deathRule must be 'knockout' or 'real'")
    locs = world.get("locations") or {}
    regions = {r.get("id") for r in world.get("regions") or []}
    for lid, loc in locs.items():
        if loc.get("type") not in LOCATION_TYPES:
            errors.append(f"{w}/map.json: {lid} type '{loc.get('type')}' should be one of {LOCATION_TYPES}")
        if loc.get("region") and loc["region"] not in regions:
            errors.append(f"{w}/map.json: {lid} is in unknown region '{loc['region']}'")
        for c in ("x", "y"):
            if not isinstance(loc.get(c), (int, float)) or not 0 <= loc[c] <= 100:
                errors.append(f"{w}/map.json: {lid}.{c} must be a number from 0 to 100")
        for sid, shop in (loc.get("shops") or {}).items():
            for i, it in enumerate(shop.get("stock") or []):
                check_item(it, f"{w}/map.json {lid}.shops.{sid}.stock[{i}]", errors)
    for i, r in enumerate(world.get("routes") or []):
        for end in ("from", "to"):
            if r.get(end) not in locs:
                errors.append(f"{w}/map.json: route {i} {end} '{r.get(end)}' isn't a location")
        if not isinstance(r.get("days"), (int, float)) or r["days"] <= 0:
            errors.append(f"{w}/map.json: route {i} needs days > 0")
        if not isinstance(r.get("danger"), int) or not 0 <= r["danger"] <= 5:
            errors.append(f"{w}/map.json: route {i} danger must be 0-5")
    if state.get("location") not in locs:
        errors.append(f"{w}/state.json: location '{state.get('location')}' isn't on the map")
    elif not locs[state["location"]].get("discovered"):
        errors.append(f"{w}/state.json: the party is at {state['location']}, so it must be discovered")
    for p in state.get("party") or []:
        pid = p.get("id")
        if not character_path(pid).exists():
            errors.append(f"{w}/state.json: party member '{pid}' has no characters/{pid}.json")
            continue
        ch = load_character(pid)
        dv = derived(ch, classes)
        if p.get("status", "ok") not in STATUSES:
            errors.append(f"{w}/state.json: {pid} status should be one of {STATUSES}")
        if p.get("hp", 0) > dv["maxHp"]:
            errors.append(f"{w}/state.json: {pid} hp {p.get('hp')} is above max {dv['maxHp']}")
        if p.get("mana", 0) > dv["maxMana"]:
            errors.append(f"{w}/state.json: {pid} mana {p.get('mana')} is above max {dv['maxMana']}")
        if p.get("status", "ok") != "away" and ch.get("activeCampaign") != cid and state.get("status") == "active":
            errors.append(f"{w}/state.json: {pid} is in the party but their activeCampaign is '{ch.get('activeCampaign')}'")


def cmd_check(args):
    classes, spells, errors = load_classes(), load_spells(), []
    if args.campaign:
        cids = [args.campaign]
        chars = [p["id"] for p in load_campaign(args.campaign)[0].get("party", [])] if (campaign_dir(args.campaign) / "state.json").exists() else []
    else:
        cids = sorted(p.name for p in CAMPAIGNS.iterdir() if p.is_dir()) if CAMPAIGNS.exists() else []
        chars = sorted(p.stem for p in CHARACTERS.glob("*.json")) if CHARACTERS.exists() else []
    for cid in chars:
        try:
            check_character(cid, load_character(cid), classes, spells, errors)
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"characters/{cid}.json: can't read: {e}")
    for cid in cids:
        check_campaign(cid, classes, errors)
    if errors:
        print("Problems found:")
        for e in errors:
            print(f"  ✖ {e}")
        sys.exit(1)
    print(f"✔ All good ({len(chars)} characters, {len(cids)} campaigns checked)")


# ---------- list / sheet / footer ----------

def cmd_list(args):
    classes = load_classes()
    print("Characters:")
    found = False
    for p in sorted(CHARACTERS.glob("*.json")):
        ch = load_json(p)
        cls = classes.get(ch.get("class"), {})
        where = f"in '{ch['activeCampaign']}'" if ch.get("activeCampaign") else "free"
        title = f" {ch['title']}" if ch.get("title") else ""
        print(f"  {cls.get('emoji', '•')} {ch.get('id')}: {ch.get('name')}{title}, {cls.get('name', ch.get('class'))} level {ch.get('level')} "
              f"(player: {ch.get('player', '?')}, {where})")
        found = True
    if not found:
        print("  (none yet)")
    print("Campaigns:")
    found = False
    for d in sorted(CAMPAIGNS.iterdir()) if CAMPAIGNS.exists() else []:
        if (d / "state.json").exists():
            s = load_json(d / "state.json")
            party = ", ".join(p["id"] for p in s.get("party", []))
            print(f"  📜 {d.name}: {s.get('title')}, {s.get('status')}, day {s.get('day')}, turn {s.get('turn')}, party: {party}")
            found = True
    if not found:
        print("  (none yet)")


def describe_item(it):
    bits = []
    if it.get("damage"):
        t = it.get("damageType", "physical")
        bits.append(f"{it['damage']} {t}" if t != "physical" else it["damage"])
    for e in it.get("extraDamage") or []:
        bits.append(f"+{e.get('dice')} {e.get('type')}")
    if it.get("armor"):
        bits.append(f"Armor {it['armor']}")
    for s, v in (it.get("stats") or {}).items():
        bits.append(f"{s.title()} {signed(int(v))}")
    for t, v in (it.get("resist") or {}).items():
        bits.append(f"Resist {t} {v}")
    for t in it.get("immune") or []:
        bits.append(f"Immune {t}")
    for t, v in (it.get("spellPower") or {}).items():
        bits.append(f"{t.title()} power +{v}")
    if it.get("hp"):
        bits.append(f"HP +{it['hp']}")
    if it.get("mana"):
        bits.append(f"Mana +{it['mana']}")
    for g in it.get("grantedSpells") or []:
        bits.append(f"casts {g.get('spell')} ({g.get('uses', '')})")
    tags = [t for t in ("twoHanded", "light", "ranged") if it.get(t)]
    bits += ["two-handed" if t == "twoHanded" else t for t in tags]
    bits += it.get("special") or []
    rar = it.get("rarity", "common")
    rar_txt = "" if rar == "common" else f" ({rar})"
    return f"{it.get('name')}{rar_txt}" + (f": {', '.join(bits)}" if bits else "")


def cmd_sheet(args):
    classes, spells = load_classes(), load_spells()
    ch = load_character(args.character)
    cls = classes.get(ch.get("class"), {})
    dv = derived(ch, classes)
    party = None
    camp = args.campaign or ch.get("activeCampaign")
    if camp and (campaign_dir(camp) / "state.json").exists():
        party = next((p for p in load_campaign(camp)[0].get("party", []) if p.get("id") == ch["id"]), None)
    title = f" {ch['title']}" if ch.get("title") else ""
    out = [f"# {cls.get('emoji', '')} {ch.get('name')}{title}",
           f"**{cls.get('name')} · Level {ch.get('level')}** · XP {ch.get('xp', 0)}/{dv['xpNext']} · Tier {dv['tier']} · Player: {ch.get('player', '?')}"]
    hp_now = f"{party.get('hp')}/" if party else ""
    mana_now = f"{party.get('mana')}/" if party else ""
    out.append(f"❤️ HP {hp_now}{dv['maxHp']} · 💧 Mana {mana_now}{dv['maxMana']} · 🛡️ Armor {dv['armor']} · 💰 {ch.get('gold', 0)} gold")
    if party and (party.get("conditions") or party.get("status", "ok") != "ok"):
        out.append(f"Status: {party.get('status', 'ok')} {', '.join(party.get('conditions') or [])}")
    out.append("")
    out.append("## Stats")
    out.append("| Stat | Base | With gear |\n|---|---|---|")
    for s in STATS:
        out.append(f"| {s.title()} | {signed(ch['stats'][s])} | **{signed(dv['stats'][s])}** |")
    defenses = [f"Resist {t} {v}" for t, v in sorted(dv["resist"].items())] + [f"Immune {t}" for t in dv["immune"]]
    if defenses or dv["spellPower"]:
        out.append("")
        if defenses:
            out.append("**Defenses:** " + ", ".join(defenses))
        if dv["spellPower"]:
            out.append("**Spell power:** " + ", ".join(f"{t} +{v}" for t, v in dv["spellPower"].items()))
    out.append("\n## Equipment")
    eq = ch.get("equipped") or {}
    labels = {"mainHand": "Main hand", "offHand": "Off hand", "ring1": "Ring", "ring2": "Ring"}
    for slot in SLOTS:
        it = eq.get(slot)
        if slot == "offHand" and isinstance(eq.get("mainHand"), dict) and eq["mainHand"].get("twoHanded"):
            txt = "(two-handed weapon)"
        else:
            txt = describe_item(it) if it else "—"
        out.append(f"- **{labels.get(slot, slot.title())}:** {txt}")
    out.append("\n## Abilities")
    for a in ch.get("abilities") or []:
        choice = f" [{a['choice']}]" if a.get("choice") else ""
        src = classes.get(a.get("source"), {}).get("abilities", {}).get(a.get("id"), {})
        uses = a.get("uses") or src.get("uses", "")
        text = a.get("text") or src.get("text", "")
        out.append(f"- **{a.get('name', a.get('id'))}**{choice} ({uses}): {text}")
    if not ch.get("abilities"):
        out.append("- —")
    out.append("\n## Spells")
    if ch.get("spells"):
        out.append("| Spell | Rank | Mastery | Cost | Element |\n|---|---|---|---|---|")
        for sp in ch["spells"]:
            meta = spells.get(sp.get("id"), {"name": sp.get("id"), "cost": "?", "element": "?", "circle": "?"})
            rank = sp.get("rank", 1)
            bonus = dv["spellPower"].get(meta["element"].lower(), 0)
            for a in ch.get("abilities") or []:
                if a.get("id") in ("elemental-affinity", "second-affinity") and str(a.get("choice", "")).lower() == meta["element"].lower():
                    bonus += 1
            eff = f" (casts as {roman(rank + bonus)})" if bonus else ""
            out.append(f"| {meta['name']} | {roman(rank)}{eff} | {sp.get('mastery', 0)}/{5 * rank} | {meta['cost']} | {meta['element']} {meta['circle']} |")
    else:
        out.append("- —")
    out.append("\n## Backpack")
    for it in ch.get("backpack") or []:
        qty = f"{it['qty']}× " if it.get("qty", 1) != 1 else ""
        out.append(f"- {qty}{describe_item(it)}")
    if not ch.get("backpack"):
        out.append("- (empty)")
    if ch.get("history"):
        out.append("\n## Legend")
        for h in ch["history"]:
            out.append(f"- **{h.get('campaign')}:** {h.get('summary', '')}")
    print("\n".join(out))


def bar(now, mx):
    return f"{now}/{mx}"


def cmd_footer(args):
    classes = load_classes()
    state, world = load_campaign(args.campaign)
    lines = ["———"]
    for p in state.get("party", []):
        ch = load_character(p["id"])
        cls = classes.get(ch.get("class"), {})
        dv = derived(ch, classes)
        st = "  ".join(f"{STAT_SHORT[s]}{signed(dv['stats'][s])}" for s in STATS)
        status = p.get("status", "ok")
        tag = {"down": " 💤DOWN", "dying": " ☠️DYING", "dead": " ⚰️DEAD", "away": " (away)"}.get(status, "")
        cond = f" · {', '.join(p['conditions'])}" if p.get("conditions") else ""
        lines.append(f"{cls.get('emoji', '•')} **{ch['name']}** {cls.get('name')} L{ch['level']}{tag} · ❤️ {bar(p.get('hp', 0), dv['maxHp'])} · "
                     f"💧 {bar(p.get('mana', 0), dv['maxMana'])} · {st} · ⭐ {ch.get('xp', 0)}/{dv['xpNext']} · 💰 {ch.get('gold', 0)}{cond}")
    loc = (world.get("locations") or {}).get(state.get("location"), {})
    quest = next((q for q in state.get("quests", []) if q.get("status") == "active"), None)
    where = f"📍 {loc.get('name', state.get('location'))} · Day {state.get('day', 1)}"
    if state.get("timeOfDay"):
        where += f", {state['timeOfDay']}"
    if quest:
        where += f" · 🎯 {quest.get('title')}"
    lines.append(where)
    combat = state.get("combat")
    if combat:
        foes = " · ".join(f"{e.get('name')} {e.get('hp')}/{e.get('maxHp')}" for e in combat.get("enemies", []) if e.get("hp", 0) > 0)
        lines.append(f"⚔️ Round {combat.get('round', 1)}: {foes}")
    print("\n".join(lines))


# ---------- map ----------

MAP_CSS = """
:root{
  /* Layout: one inked chart of the realm on top; beneath it, a ledger of known places read from the party's position. */
  --paper:#e6eadf; --paper-2:#dbe0d2; --ink:#262b25; --ink-soft:#59614f; --rule:#a4ab98;
  --pin:#3b3f8c; --pin-soft:rgba(59,63,140,.18);
  --safe:#3f7d47; --risky:#a2701b; --deadly:#9e3a30;
  --r1:#8fae72; --r2:#86a1bd; --r3:#cdb98a; --r4:#b49cc0; --r5:#c49a86; --r6:#8fb6ad;
  --font-display:"IM Fell English SC", "Iowan Old Style", Georgia, serif;
  --font-script:"IM Fell English", "Iowan Old Style", Georgia, serif;
  --font-body:"Alegreya Sans", "Gill Sans", "Segoe UI", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --paper:#141a1e; --paper-2:#1b2328; --ink:#dfe5d8; --ink-soft:#97a393; --rule:#4a5650;
  --pin:#a9afff; --pin-soft:rgba(169,175,255,.2);
  --safe:#7cc184; --risky:#e2b35a; --deadly:#ec8277;
  --r1:#4f6b3e; --r2:#3f5a77; --r3:#6f6243; --r4:#5e4a6c; --r5:#6c4c40; --r6:#3e6760; color-scheme:dark}}
:root[data-theme="dark"]{
  --paper:#141a1e; --paper-2:#1b2328; --ink:#dfe5d8; --ink-soft:#97a393; --rule:#4a5650;
  --pin:#a9afff; --pin-soft:rgba(169,175,255,.2);
  --safe:#7cc184; --risky:#e2b35a; --deadly:#ec8277;
  --r1:#4f6b3e; --r2:#3f5a77; --r3:#6f6243; --r4:#5e4a6c; --r5:#6c4c40; --r6:#3e6760; color-scheme:dark}
body{background:var(--paper);color:var(--ink);font-family:var(--font-body);font-size:16px;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding-block:20px 48px;padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));display:grid;gap:24px}
header{display:grid;gap:4px}
.eyebrow{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft)}
h1{font-family:var(--font-display);font-weight:400;font-size:clamp(1.9rem,5vw,3rem);line-height:1.05;margin:0;text-wrap:balance}
.where{font-family:var(--font-script);font-style:italic;font-size:1.1rem;color:var(--ink-soft);margin:0}
.chart{border:1px solid var(--rule);background:var(--paper-2);border-radius:2px;overflow:hidden}
.chart-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.chart svg{display:block;width:100%;min-width:720px;height:auto}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:.85rem;color:var(--ink-soft);padding:10px 14px;border-top:1px solid var(--rule)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend svg{width:18px;height:12px}
h2{font-family:var(--font-display);font-weight:400;font-size:1.5rem;margin:0}
.places{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:12px}
.place{border-top:2px solid var(--rule);padding-top:10px;display:grid;gap:6px;min-width:0}
.place.here{border-top-color:var(--pin)}
.place h3{font-family:var(--font-display);font-weight:400;font-size:1.25rem;margin:0;display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.kind{font-family:var(--font-body);font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft);white-space:nowrap}
.place p{margin:0;max-width:65ch}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{font-size:.8rem;border:1px solid var(--rule);border-radius:999px;padding:1px 9px;color:var(--ink)}
.here-tag{color:var(--pin);font-weight:700}
.unvisited{font-style:italic;color:var(--ink-soft)}
.routes{font-size:.9rem;color:var(--ink-soft);font-variant-numeric:tabular-nums}
.d0,.d1,.d2{color:var(--safe)} .d3{color:var(--risky)} .d4,.d5{color:var(--deadly)}
.note{font-size:.9rem;color:var(--ink-soft)}
.svg-ink{fill:var(--ink)} .svg-soft{fill:var(--ink-soft)}
@media (prefers-reduced-motion: no-preference){.pulse{animation:pulse 2.4s ease-in-out infinite;transform-origin:center;transform-box:fill-box}
@keyframes pulse{0%,100%{opacity:.85;transform:scale(1)}50%{opacity:.35;transform:scale(1.35)}}}
"""

W, H, PAD = 1000, 640, 60


def mx(x):
    return PAD + x / 100 * (W - 2 * PAD)


def my(y):
    return PAD + y / 100 * (H - 2 * PAD)


def marker(kind, x, y, visited):
    """SVG marker for a location type. Visited places are solid, heard-of places are hollow."""
    fill = "var(--ink)" if visited else "var(--paper-2)"
    s = 'stroke="var(--ink)" stroke-width="2"'
    if kind == "city":
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="var(--paper-2)" {s}/>'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{fill}" {s}/>')
    if kind == "town":
        return f'<rect x="{x - 7:.1f}" y="{y - 7:.1f}" width="14" height="14" fill="{fill}" {s}/>'
    if kind == "village":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{fill}" {s}/>'
    if kind in ("dungeon", "ruin"):
        dash = ' stroke-dasharray="3 2"' if kind == "ruin" else ""
        return f'<path d="M{x:.1f},{y - 9:.1f} L{x + 9:.1f},{y + 7:.1f} L{x - 9:.1f},{y + 7:.1f} Z" fill="{fill}" {s}{dash}/>'
    if kind == "camp":
        return f'<path d="M{x - 8:.1f},{y + 7:.1f} L{x:.1f},{y - 8:.1f} L{x + 8:.1f},{y + 7:.1f} M{x:.1f},{y - 8:.1f} L{x:.1f},{y + 7:.1f}" fill="none" {s}/>'
    return f'<path d="M{x:.1f},{y - 9:.1f} L{x + 8:.1f},{y:.1f} L{x:.1f},{y + 9:.1f} L{x - 8:.1f},{y:.1f} Z" fill="{fill}" {s}/>'


def danger_class(d):
    return "var(--safe)" if d <= 2 else "var(--risky)" if d == 3 else "var(--deadly)"


def days_txt(d):
    return f"{d:g} day" + ("" if d == 1 else "s")


def danger_word(d):
    return ["safe", "quiet", "watchful", "risky", "dangerous", "deadly"][max(0, min(5, d))]


def build_map_html(cid):
    state, world = load_campaign(cid)
    e = html.escape
    locs = world.get("locations") or {}
    known = {k: v for k, v in locs.items() if v.get("discovered")}
    here = state.get("location")
    region_tok = {}
    for i, r in enumerate(world.get("regions") or []):
        region_tok[r["id"]] = (r.get("name", r["id"]), f"var(--r{i % 6 + 1})")

    svg = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Map of the known world">']
    # land wash: soft overlapping blobs around each known place, tinted by region
    svg.append('<defs><filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter></defs>')
    svg.append('<g filter="url(#soft)" opacity=".55">')
    for lid, loc in known.items():
        tint = region_tok.get(loc.get("region"), ("", "var(--r1)"))[1]
        svg.append(f'<circle cx="{mx(loc["x"]):.1f}" cy="{my(loc["y"]):.1f}" r="95" fill="{tint}"/>')
    svg.append("</g>")
    # frame and compass
    svg.append(f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" fill="none" stroke="var(--rule)" stroke-width="1"/>')
    cx, cy = W - 70, H - 78
    svg.append(f'<g aria-hidden="true"><circle cx="{cx}" cy="{cy}" r="26" fill="none" stroke="var(--rule)"/>'
               f'<path d="M{cx},{cy - 34} L{cx + 6},{cy} L{cx},{cy + 34} L{cx - 6},{cy} Z" fill="var(--ink-soft)"/>'
               f'<path d="M{cx - 34},{cy} L{cx},{cy - 5} L{cx + 34},{cy} L{cx},{cy + 5} Z" fill="var(--rule)"/>'
               f'<text x="{cx}" y="{cy - 40}" text-anchor="middle" class="svg-ink" font-family="var(--font-display)" font-size="16">N</text></g>')
    # region names at the centre of their known places
    for rid, (rname, _) in region_tok.items():
        pts = [(mx(l["x"]), my(l["y"])) for l in known.values() if l.get("region") == rid]
        if not pts:
            continue
        rx = sum(p[0] for p in pts) / len(pts)
        ry = min(H - 30, sum(p[1] for p in pts) / len(pts) + 56)
        svg.append(f'<text x="{rx:.1f}" y="{ry:.1f}" text-anchor="middle" class="svg-soft" font-family="var(--font-script)" '
                   f'font-style="italic" font-size="22" letter-spacing="6" opacity=".8">{e(rname.upper())}</text>')
    # routes between known places
    for r in world.get("routes") or []:
        a, b = known.get(r.get("from")), known.get(r.get("to"))
        if not a or not b:
            continue
        x1, y1, x2, y2 = mx(a["x"]), my(a["y"]), mx(b["x"]), my(b["y"])
        road = "road" in str(r.get("terrain", "")).lower()
        dash = "" if road else ' stroke-dasharray="7 6"'
        col = danger_class(int(r.get("danger", 0)))
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="2.2" stroke-linecap="round"{dash} opacity=".9"/>')
        days = r.get("days")
        label = f"{days:g}d" if isinstance(days, (int, float)) else ""
        svg.append(f'<text x="{(x1 + x2) / 2:.1f}" y="{(y1 + y2) / 2 - 6:.1f}" text-anchor="middle" font-family="var(--font-body)" font-size="13" '
                   f'fill="{col}" stroke="var(--paper-2)" stroke-width="4" paint-order="stroke" font-weight="700">{e(label)}</text>')
    # places
    for lid, loc in known.items():
        x, y = mx(loc["x"]), my(loc["y"])
        if lid == here:
            svg.append(f'<circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="20" fill="var(--pin-soft)" stroke="var(--pin)" stroke-width="2"/>')
        svg.append(marker(loc.get("type"), x, y, loc.get("visited")))
        size = 21 if loc.get("type") == "city" else 17
        weight = ' font-weight="400"'
        anchor = "end" if loc["x"] > 82 else "start" if loc["x"] < 18 else "middle"
        tx = x - 16 if anchor == "end" else x + 16 if anchor == "start" else x
        ty = y + 5 if anchor != "middle" else y - 18
        svg.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" class="svg-ink" font-family="var(--font-display)" font-size="{size}"{weight} '
                   f'stroke="var(--paper-2)" stroke-width="5" paint-order="stroke">{e(loc.get("name", lid))}</text>')
        if lid == here:
            svg.append(f'<text x="{x:.1f}" y="{y + 34:.1f}" text-anchor="middle" fill="var(--pin)" font-family="var(--font-body)" font-size="13" '
                       f'font-weight="700" letter-spacing="2" stroke="var(--paper-2)" stroke-width="4" paint-order="stroke">YOU ARE HERE</text>')
    svg.append("</svg>")

    def routes_from(lid):
        out = []
        for r in world.get("routes") or []:
            other = r["to"] if r.get("from") == lid else r["from"] if r.get("to") == lid else None
            if other and other in known:
                d = int(r.get("danger", 0))
                out.append(f'<span class="d{d}">{e(known[other].get("name", other))} · {days_txt(r.get("days"))} · {e(r.get("terrain", ""))} · {danger_word(d)}</span>')
        return out

    order = sorted(known, key=lambda k: (k != here, not known[k].get("visited"), known[k].get("name", k)))
    cards = []
    for lid in order:
        loc = known[lid]
        kind = e(loc.get("type", ""))
        region = region_tok.get(loc.get("region"), ("", ""))[0]
        status = '<span class="here-tag">You are here</span>' if lid == here else (
            "Visited" if loc.get("visited") else '<span class="unvisited">Heard of, not yet visited</span>')
        chips = "".join(f'<span class="chip">{e(s.split(":")[0].replace("-", " "))}{" · " + e(s.split(":", 1)[1]) if ":" in s else ""}</span>'
                        for s in loc.get("services") or []) if loc.get("visited") else ""
        notes = "".join(f'<p class="note">• {e(n)}</p>' for n in loc.get("notes") or [])
        rts = routes_from(lid)
        cards.append(
            f'<article class="place{" here" if lid == here else ""}"><h3>{e(loc.get("name", lid))}<span class="kind">{kind}{" · " + e(region) if region else ""}</span></h3>'
            f'<div class="note">{status}</div>'
            f'<p>{e(loc.get("description", ""))}</p>'
            + (f'<div class="chips">{chips}</div>' if chips else "")
            + notes
            + (f'<div class="routes">{"<br>".join(rts)}</div>' if rts else "")
            + "</article>")

    here_loc = known.get(here, {})
    unknown = len(locs) - len(known)
    leg = [
        ('<svg viewBox="0 0 18 12"><circle cx="9" cy="6" r="5" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/><circle cx="9" cy="6" r="2.5" fill="var(--ink)"/></svg>', "City"),
        ('<svg viewBox="0 0 18 12"><rect x="4" y="1" width="10" height="10" fill="var(--ink)"/></svg>', "Town"),
        ('<svg viewBox="0 0 18 12"><circle cx="9" cy="6" r="4" fill="var(--ink)"/></svg>', "Village"),
        ('<svg viewBox="0 0 18 12"><path d="M9,1 L15,11 L3,11 Z" fill="var(--ink)"/></svg>', "Dungeon / ruin"),
        ('<svg viewBox="0 0 18 12"><path d="M9,0 L15,6 L9,12 L3,6 Z" fill="var(--ink)"/></svg>', "Landmark"),
        ('<svg viewBox="0 0 18 12"><circle cx="9" cy="6" r="4" fill="var(--paper-2)" stroke="var(--ink)" stroke-width="1.5"/></svg>', "Hollow: not yet visited"),
        ('<svg viewBox="0 0 18 12"><line x1="1" y1="6" x2="17" y2="6" stroke="var(--ink-soft)" stroke-width="2"/></svg>', "Road"),
        ('<svg viewBox="0 0 18 12"><line x1="1" y1="6" x2="17" y2="6" stroke="var(--ink-soft)" stroke-width="2" stroke-dasharray="4 3"/></svg>', "Wild path · days to travel"),
        ('<svg viewBox="0 0 18 12"><line x1="1" y1="6" x2="17" y2="6" stroke="var(--safe)" stroke-width="3"/></svg>', "Safe"),
        ('<svg viewBox="0 0 18 12"><line x1="1" y1="6" x2="17" y2="6" stroke="var(--risky)" stroke-width="3"/></svg>', "Risky"),
        ('<svg viewBox="0 0 18 12"><line x1="1" y1="6" x2="17" y2="6" stroke="var(--deadly)" stroke-width="3"/></svg>', "Dangerous"),
    ]
    legend = "".join(f"<span>{s}{e(t)}</span>" for s, t in leg)
    title = state.get("title", cid)
    page = f"""<title>{e(title)} Atlas</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IM+Fell+English+SC&family=IM+Fell+English:ital@0;1&family=Alegreya+Sans:wght@400;700&display=swap">
<style>{MAP_CSS}</style>
<div class="wrap">
<header>
  <div class="eyebrow">{e(state.get("setting", "The known world"))}</div>
  <h1>{e(title)}</h1>
  <p class="where">The party is at {e(here_loc.get("name", here or "?"))} · Day {state.get("day", 1)}{(", " + e(state["timeOfDay"])) if state.get("timeOfDay") else ""}</p>
</header>
<figure class="chart" style="margin:0">
  <div class="chart-scroll">{"".join(svg)}</div>
  <figcaption class="legend">{legend}</figcaption>
</figure>
<section style="display:grid;gap:14px">
  <h2>Known places</h2>
  <div class="places">{"".join(cards)}</div>
  <p class="note">{"Somewhere beyond the edges, " + str(unknown) + " more place" + ("s wait" if unknown != 1 else " waits") + " to be found." if unknown else "Every place in this land has been found."}</p>
</section>
</div>
"""
    return page


def cmd_map(args):
    out = Path(args.output) if args.output else campaign_dir(args.campaign) / "map.html"
    out.write_text(build_map_html(args.campaign), encoding="utf-8")
    print(f"✔ Map written to {out.relative_to(ROOT) if out.is_absolute() and ROOT in out.parents else out}")


# ---------- sync ----------

def git(*a, check=True):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r


def cmd_sync(args):
    """Bring in the newest save from any branch, so a new session continues where the last one stopped."""
    if git("status", "--porcelain").stdout.strip():
        print("✖ There are unsaved changes here. Commit them first (they may be a save in progress).")
        sys.exit(1)
    fetched = git("fetch", "origin", "+refs/heads/*:refs/remotes/origin/*", "--prune", check=False)
    if fetched.returncode != 0:
        print(f"⚠ Couldn't reach GitHub: {fetched.stderr.strip()}\n  Playing from the saves already here.")
        return
    best = None
    for ref in git("for-each-ref", "--format=%(refname)", "refs/remotes/origin").stdout.split():
        if ref.endswith("/HEAD"):
            continue
        line = git("log", "-1", "--format=%ct %H %s", "-F", "--grep=[save]", ref, check=False).stdout.strip()
        if line:
            ts, sha, subject = line.split(" ", 2)
            if not best or int(ts) > best[0]:
                best = (int(ts), sha, subject, ref.replace("refs/remotes/origin/", ""))
    if not best:
        print("✔ No saves found anywhere yet. Fresh start.")
        return
    ts, sha, subject, branch = best
    if git("merge-base", "--is-ancestor", sha, "HEAD", check=False).returncode == 0:
        print(f"✔ Up to date. Latest save: \"{subject}\"")
        return
    r = git("merge", "--no-edit", "-m", f"Load latest save from {branch}", sha, check=False)
    if r.returncode != 0:
        git("merge", "--abort", check=False)
        print(f"✖ The latest save on '{branch}' (\"{subject}\") conflicts with this branch.\n"
              f"  Nothing was changed. Ask the DM to resolve it, or start the session from '{branch}'.")
        sys.exit(1)
    print(f"✔ Loaded latest save from '{branch}': \"{subject}\"")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser(description="AI&D game helper")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("roll", help="roll dice, e.g. d20+3 2d6")
    p.add_argument("dice", nargs="+")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--adv", action="store_true", help="advantage: roll d20 twice, keep higher")
    g.add_argument("--dis", action="store_true", help="disadvantage: roll d20 twice, keep lower")
    p.add_argument("--label", help="what the roll is for")
    p.set_defaults(fn=cmd_roll)
    p = sub.add_parser("list", help="list characters and campaigns")
    p.set_defaults(fn=cmd_list)
    p = sub.add_parser("check", help="validate characters and campaigns")
    p.add_argument("campaign", nargs="?")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("sheet", help="print a character sheet")
    p.add_argument("character")
    p.add_argument("--campaign")
    p.set_defaults(fn=cmd_sheet)
    p = sub.add_parser("footer", help="print the stats footer for a campaign")
    p.add_argument("campaign")
    p.set_defaults(fn=cmd_footer)
    p = sub.add_parser("map", help="draw the campaign map as an HTML page")
    p.add_argument("campaign")
    p.add_argument("-o", "--output")
    p.set_defaults(fn=cmd_map)
    p = sub.add_parser("sync", help="load the newest save from any branch")
    p.set_defaults(fn=cmd_sync)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
