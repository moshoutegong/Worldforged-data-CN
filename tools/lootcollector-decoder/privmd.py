import pickle, re, sys
L = "C:/Users/USER/AppData/Local/Temp/claude/C--CLAUDE/c1d4531f-f6e2-4f95-9dca-17d7cefc226a/scratchpad/lc"
allp = pickle.load(open(L + "/parsed.pkl", "rb")); items = pickle.load(open(L + "/items.pkl", "rb")); wma = pickle.load(open(L + "/wma.pkl", "rb"))
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
for t in items["tsv"].values(): vocab |= {w.lower() for w in TOK.findall(t.get("name", ""))}
for w in wma["captured"].values(): vocab |= {x.lower() for x in TOK.findall(w["name"])}
for fn in sys.argv[1:]:
    hits = []
    for ln, line in enumerate(open(fn, encoding="utf-8", errors="replace"), 1):
        for t in {x.lower() for x in TOK.findall(line)} & names:
            hits.append((ln, len(t), t in vocab))
    print(fn.split("/")[-1], "hits", len(hits), "| in game vocab", sum(h[2] for h in hits), "| NOT in game vocab (line, len):", [(a, b) for a, b, c in hits if not c])
