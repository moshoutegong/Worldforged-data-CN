"""Build the Exiles (db.exil.es mirror) Worldforged tier ladder as one CSV.

Source: the Exiles item pages already parsed to p_item.jsonl (13,953 pages say "Source: Worldforged", each
with a Tier label), joined to S1's union itemcache for the item level of every tier id.
One row per (name, tier, id). Game data only: no player, account or finder fields exist in these inputs.
Read-only on every input. Output: data/exiles_wf_ladder.csv next to this repo's README.
"""
import collections
import csv
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "exiles_wf_ladder.csv")
P_ITEM = (r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a"
          r"\scratchpad\exiles\loot-quests\p_item.jsonl")
S1 = r"D:\acore-classless\build\design\ext-sources\S1-ascension-data\cachedata\union\itemcache.tsv.gz"
ORDER = ["Base", "Lvl", "MC", "ZG", "BWL", "AQ40", "Naxx"]
TIER_LABEL = {"Base": "Base", "Lvl": "Lvl 60", "MC": "Molten Core", "ZG": "Zul'Gurub", "BWL": "Blackwing Lair",
              "AQ40": "AQ40", "Naxx": "Naxxramas"}

wf = {}
for line in open(P_ITEM, encoding="utf-8"):
    r = json.loads(line)
    if r["summary"].get("Source") == "Worldforged":
        tier = (r["summary"].get("Tier") or "").split(" ")[0]
        wf[r["id"]] = (r["name"], tier, r["summary"].get("Found at") or r["summary"].get("Found At") or "")

csv.field_size_limit(1 << 30)
ilvl, req = {}, {}
with gzip.open(S1, "rt", encoding="utf-8", newline="") as f:
    rd = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
    hdr = next(rd)
    ix = {h: k for k, h in enumerate(hdr)}
    rl = next((c for c in hdr if c.lower() in ("requiredlevel", "reqlevel", "required_level")), None)
    for row in rd:
        if not row:
            continue
        e = int(row[0])
        if e in wf:
            ilvl[e] = int(row[ix["ItemLevel"]] or 0)
            if rl:
                req[e] = row[ix[rl]]

by_name = collections.defaultdict(list)
for i, (n, t, found) in wf.items():
    by_name[n].append((ORDER.index(t) if t in ORDER else 99, t, i, found))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
n_rows = 0
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["name", "tier", "tier_label", "item_id", "s1_item_level", "s1_required_level", "found_at_zone",
                "name_has_all_7_tiers"])
    for name in sorted(by_name):
        rows = sorted(by_name[name])
        full = len({t for _, t, _, _ in rows} & set(ORDER)) == 7
        for _, t, i, found in rows:
            w.writerow([name, t, TIER_LABEL.get(t, t), i, ilvl.get(i, ""), req.get(i, ""), found, int(full)])
            n_rows += 1

full_names = sum(1 for n, rows in by_name.items() if len({t for _, t, _, _ in rows} & set(ORDER)) == 7)
print(f"wrote {OUT}: {n_rows} rows, {len(by_name)} names, {full_names} names with all 7 tiers, "
      f"{sum(1 for i in wf if i in ilvl)} of {len(wf)} ids with an S1 item level")
