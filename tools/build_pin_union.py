"""Master Worldforged pickup-location union: StarterDB + Discord-dump zips + Discord-dump RARs, one CSV.

Sources (all read-only, all read in memory):
  S  our installed client's LootCollector_StarterDB (decoded by scratchpad/verdict/starterdecode.py)
  Z  the Discord dump's .zip LootCollector copies (lua + bak)
  R  the Discord dump's .rar LootCollector copies (lua + bak), streamed with 7-Zip (never extracted)
Pins are Worldforged discoveries (dt == 1), deduped per (item, zone) at 0.005 map units -- the method the
Discord verdict used. Map-percent coords are converted to server X/Y with Ascension's captured WorldMapArea
bounds (X = Top - y*(Top-Bottom), Y = Left - x*(Left-Right); z = WMA id + 1), verified on 32,485 spawns.

PRIVACY: LootCollector records also carry finder/originator/voter names. This script reads ONLY the numeric
fields dt, i, z, x, y from each record and writes only game data (item, zone, coordinates, source flags).
A pin is the LOOTER's position at pickup time (median 3.5 yd from the spawn), not the spawn point. Z is absent.

Outputs: data/wf_pins_union.csv and data/wf_items_union.csv.
"""
import collections
import contextlib
import csv
import gzip
import importlib.util
import io
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SP = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad"
S1 = r"D:\acore-classless\build\design\ext-sources\S1-ascension-data\cachedata\union\itemcache.tsv.gz"
sys.path.insert(0, SP)
from dumpio import ROOT, is_archive, members, stream  # noqa: E402

spec = importlib.util.spec_from_file_location("sd", os.path.join(SP, "verdict", "starterdecode.py"))
sd = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(sd)
wma = pickle.load(open(os.path.join(SP, "lc", "wma.pkl"), "rb"))["captured"]

REC = re.compile(rb'\[\s*"(\d+-\d+-\d+-\d+-[-0-9.]+)"\s*\]\s*=\s*\{')
F = {k: re.compile(rb'\[\s*"' + k + rb'"\s*\]\s*=\s*(-?[0-9.]+)') for k in (b"dt", b"i", b"z", b"x", b"y")}


def is_lc(p):
    return os.path.basename(p).lower() in ("lootcollector.lua", "lootcollector.lua.bak")


def records(blob):
    starts = list(REC.finditer(blob))
    for n, m in enumerate(starts):
        end = starts[n + 1].start() if n + 1 < len(starts) else min(len(blob), m.end() + 4000)
        body = blob[m.end():end]
        v = {k: (rx.search(body).group(1) if rx.search(body) else None) for k, rx in F.items()}
        try:
            yield int(v[b"i"]), int(v[b"z"]), float(v[b"x"]), float(v[b"y"]), int(float(v[b"dt"]))
        except (TypeError, ValueError):
            continue


# pins[(item, zone)] -> list of dict(x, y, src=set, n)
pins = collections.defaultdict(list)


def add(it, z, x, y, src):
    lst = pins[(it, z)]
    for p in lst:
        if abs(x - p["x"]) <= 0.005 and abs(y - p["y"]) <= 0.005:
            p["src"].add(src)
            p["n"] += 1
            return False
    lst.append({"x": x, "y": y, "src": {src}, "n": 1})
    return True


added = collections.Counter()
for it, z, x, y, dt in sd.S:
    if dt == 1 and it and z and x is not None and y is not None:
        added["S"] += add(it, z, x, y, "S")
# zips first, then rars, so the incremental counts match DISCORD-DUMP-VERDICT section 9 (S -> +Z -> +R)
for ext, g in ((".zip", "Z"), (".rar", "R")):
    for f in sorted(os.listdir(ROOT)):
        if not is_archive(f) or not f.lower().endswith(ext):
            continue
        p = os.path.join(ROOT, f)
        if not any(is_lc(n) for n, _ in members(p)):
            continue
        for _, blob in stream(p, want=is_lc):
            for it, z, x, y, dt in records(blob):
                if dt == 1:
                    added[g] += add(it, z, x, y, g)

item_ids = {it for it, _ in pins}
csv.field_size_limit(1 << 30)
name, ilvl, req = {}, {}, {}
with gzip.open(S1, "rt", encoding="utf-8", newline="") as fh:
    rd = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
    hdr = next(rd)
    ix = {h.lower(): k for k, h in enumerate(hdr)}
    nc = ix.get("name"); lc = ix.get("itemlevel"); rc = next((ix[c] for c in ("requiredlevel", "reqlevel", "required_level") if c in ix), None)
    for row in rd:
        if row and row[0].isdigit() and int(row[0]) in item_ids:
            e = int(row[0])
            if nc is not None: name[e] = row[nc]
            if lc is not None: ilvl[e] = row[lc]
            if rc is not None: req[e] = row[rc]

os.makedirs(DATA, exist_ok=True)
per_item = collections.defaultdict(lambda: {"n": 0, "S": 0, "Z": 0, "R": 0, "maps": set(), "zones": set()})
n_pins = 0
with open(os.path.join(DATA, "wf_pins_union.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["item_id", "item_name", "s1_item_level", "s1_required_level", "lc_z", "wma_id", "wma_name",
                "server_map", "norm_x", "norm_y", "server_X", "server_Y", "in_starterdb", "in_dump_zip",
                "in_dump_rar", "n_records"])
    for (it, z), lst in sorted(pins.items()):
        wm = wma.get(z - 1) or {}
        for p in lst:
            X = Y = ""
            if wm:
                X = round(wm["T"] - p["y"] * (wm["T"] - wm["B"]), 1)
                Y = round(wm["L"] - p["x"] * (wm["L"] - wm["R"]), 1)
            w.writerow([it, name.get(it, ""), ilvl.get(it, ""), req.get(it, ""), z, z - 1, wm.get("name", ""),
                        wm.get("map", ""), round(p["x"], 4), round(p["y"], 4), X, Y,
                        int("S" in p["src"]), int("Z" in p["src"]), int("R" in p["src"]), p["n"]])
            n_pins += 1
            d = per_item[it]
            d["n"] += 1
            for s in p["src"]:
                d[s] += 1
            if wm:
                d["maps"].add(str(wm.get("map", "")))
                d["zones"].add(str(wm.get("name", "")))

with open(os.path.join(DATA, "wf_items_union.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["item_id", "item_name", "s1_item_level", "s1_required_level", "n_pins", "n_pins_starterdb",
                "n_pins_dump_zip", "n_pins_dump_rar", "server_maps", "zones"])
    for it in sorted(per_item):
        d = per_item[it]
        w.writerow([it, name.get(it, ""), ilvl.get(it, ""), req.get(it, ""), d["n"], d["S"], d["Z"], d["R"],
                    "|".join(sorted(d["maps"])), "|".join(sorted(d["zones"]))])

only = collections.Counter()
for lst in pins.values():
    for p in lst:
        only[tuple(sorted(p["src"]))] += 1
print(f"pins {n_pins:,} over {len(per_item):,} items | added in order S {added['S']:,}, +Z {added['Z']:,}, +R {added['R']:,}")
print("pin source sets:", dict(only))
print(f"items named from S1: {sum(1 for i in per_item if i in name):,} of {len(per_item):,}")
maps = collections.Counter()
for (it, z), lst in pins.items():
    wm = wma.get(z - 1) or {}
    maps[wm.get("map", "?")] += len(lst)
print("pins by server map:", dict(maps.most_common(8)))
