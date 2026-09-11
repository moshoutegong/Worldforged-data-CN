import pickle, re, csv, collections
L = "C:/Users/USER/AppData/Local/Temp/claude/C--CLAUDE/c1d4531f-f6e2-4f95-9dca-17d7cefc226a/scratchpad/lc"
allp = pickle.load(open(L + "/parsed.pkl", "rb"))
items = pickle.load(open(L + "/items.pkl", "rb"))
wma = pickle.load(open(L + "/wma.pkl", "rb"))
names = set()
for (z, p), sv in allp.items():
    db = sv["LootCollectorDB_Asc"]
    for k in list(db.get("char", {})) + list(db.get("profileKeys", {})):
        names.add(str(k).split(" - ")[0].strip().lower())
    for rv in db["global"].get("realms", {}).values():
        for r in list(rv.get("discoveries", {}).values()) + list(rv.get("blackmarketVendors", {}).values()):
            for f in ("fp", "o"):
                if isinstance(r.get(f), str): names.add(r[f].strip().lower())
            for f in ("fp_votes", "ack_votes"):
                if isinstance(r.get(f), dict): names |= {str(x).strip().lower() for x in r[f]}
names = {n for n in names if len(n) >= 3 and n != "an unnamed collector"}
TOK = re.compile(r"[^\W\d_][\w'\-]*")
vocab = set()
for t in items["tsv"].values():
    vocab |= {w.lower() for w in TOK.findall(t.get("name", ""))}
for w in wma["captured"].values():
    vocab |= {x.lower() for x in TOK.findall(w["name"])}
bycol = collections.Counter(); game = 0; notgame = 0
hdr = None
for ln, row in enumerate(csv.reader(open(L + "/wf_locations.csv", encoding="utf-8")), 1):
    if ln == 1: hdr = row; continue
    for ci, cell in enumerate(row):
        for t in {x.lower() for x in TOK.findall(cell)} & names:
            bycol[hdr[ci]] += 1
            if t in vocab: game += 1
            else: notgame += 1
print("hits by column:", dict(bycol), "| token also in itemcache/WMA game vocabulary:", game, "| NOT in game vocab:", notgame)
