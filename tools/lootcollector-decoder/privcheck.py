"""Scan output files for any person-name value from the LootCollector SVs. Prints ONLY counts and
line numbers -- never the matched value."""
import sys, pickle, re
L = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc"
allp = pickle.load(open(L + r"\parsed.pkl", 'rb'))
names = set()
for (z, p), sv in allp.items():
    db = sv['LootCollectorDB_Asc']
    for k in list(db.get('char', {})) + list(db.get('profileKeys', {})):
        names.add(str(k).split(' - ')[0].strip())
    for rv in db['global'].get('realms', {}).values():
        for r in list(rv.get('discoveries', {}).values()) + list(rv.get('blackmarketVendors', {}).values()):
            for f in ('fp', 'o'):
                if isinstance(r.get(f), str):
                    names.add(r[f].strip())
            for f in ('fp_votes', 'ack_votes'):
                if isinstance(r.get(f), dict):
                    names |= {str(x).strip() for x in r[f]}
names = {n for n in names if len(n) >= 3 and n != 'An Unnamed Collector'}
print('person-name values loaded:', len(names))
pat = {n.lower() for n in names}
for fn in sys.argv[1:]:
    hits = []
    for ln, line in enumerate(open(fn, encoding='utf-8', errors='replace'), 1):
        toks = set(t.lower() for t in re.findall(r"[^\W\d_][\w'\-]*", line))
        for t in toks & pat:
            hits.append((ln, len(t)))
    print(fn, 'hits', len(hits), 'at (line, token length):', hits[:60])
