import pickle, csv, collections, re
L = "C:/Users/USER/AppData/Local/Temp/claude/C--CLAUDE/c1d4531f-f6e2-4f95-9dca-17d7cefc226a/scratchpad/lc"
DES = "D:/acore-classless/build/design"
m = pickle.load(open(L + "/main.pkl", "rb")); items = pickle.load(open(L + "/items.pkl", "rb"))
wma = pickle.load(open(L + "/wma.pkl", "rb")); allp = pickle.load(open(L + "/parsed.pkl", "rb"))
cap, stock, tsv = wma["captured"], wma["stock"], items["tsv"]
cached = {int(x) for x in open(DES + "/zones-item-ids.txt").read().replace("\n", ",").split(",") if x.strip()}
rows = m["csvrows"]; uniq = m["uniq"]
zs = {r[5] for r in rows}
print("WF distinct z", len(zs), "| stock WMA", sum(1 for z in zs if z - 1 in stock), "| Ascension-custom WMA", sum(1 for z in zs if z - 1 not in stock))
for tag, sel in (("stockWMA", lambda r: r[6] in stock), ("customWMA", lambda r: r[6] not in stock)):
    d = sorted(float(r[14]) for r in rows if sel(r) and r[14] != "")
    n = sum(1 for r in rows if sel(r))
    if d: print("%s pins %d with GO %d: nearest GO median %.1f | <=5yd %d | <=10yd %d" % (tag, n, len(d), d[len(d)//2], sum(x <= 5 for x in d), sum(x <= 10 for x in d)))
cont = {0, 1, 530, 571}
inst = [r for r in rows if r[8] not in cont]
print("WF pins on non-continent (instance) maps:", len(inst), "maps", len({r[8] for r in inst}))
msn = {r["i"] for r in uniq.values() if r["dt"] == 2}; allit = {r["i"] for r in uniq.values()}
none = allit - cached - set(tsv)
print("items in none:", len(none), "of which Mystic Scroll dt2:", len(none & msn))
vt = collections.Counter()
for (z, p), sv in allp.items():
    for rv in sv["LootCollectorDB_Asc"]["global"].get("realms", {}).values():
        for r in rv.get("blackmarketVendors", {}).values():
            vt[r.get("vendorType")] += 1
assert len(vt) <= 10
print("blackmarketVendors vendorType:", dict(vt))
# per-item sidecar
per = collections.defaultdict(lambda: dict(pins=0, zones=set(), maps=set(), realms=0, go5=0))
for r in rows:
    a = per[r[0]]; a["pins"] += 1; a["zones"].add(r[7]); a["maps"].add(r[8]); a["realms"] = max(a["realms"], r[16])
    if r[14] != "" and float(r[14]) <= 5: a["go5"] += 1
NAME = re.compile(r"\|h\[(.*?)\]\|h")
nm = {}
for r in uniq.values():
    mm = NAME.search(r["il"]); nm.setdefault(r["i"], mm.group(1) if mm else "")
with open(L + "/wf_items.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["item_id", "item_name", "item_level", "req_level", "quality", "class", "subclass", "inv_type", "n_pins", "n_pins_go_within_5yd", "server_maps", "zones", "in_our_55454_cache", "in_harvest_itemcache"])
    for i in sorted(per):
        t = tsv.get(i, {}); a = per[i]
        w.writerow([i, nm.get(i, ""), t.get("itemLevel", ""), t.get("reqLevel", ""), t.get("quality", ""), t.get("class", ""), t.get("subclass", ""), t.get("invType", ""), a["pins"], a["go5"], "|".join(str(x) for x in sorted(a["maps"])), "|".join(sorted(a["zones"])), int(i in cached), int(i in tsv)])
print("wf_items rows", len(per))
