"""Collect every item id LootCollector references, then stream the largest harvest itemcache TSV
(in memory, from the zip) and keep only matching rows. Item names are game data, not personal data."""
import pickle, re, zipfile, io, collections
PK = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\parsed.pkl"
OUT = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\items.pkl"
allp = pickle.load(open(PK, 'rb'))
HIT = re.compile(r'Hitem:(\d+)')
ids = collections.defaultdict(set)
vend_shapes = collections.Counter()
for (z, p), sv in allp.items():
    g = sv['LootCollectorDB_Asc']['global']
    for rk, rv in g.get('realms', {}).items():
        for k, r in rv.get('discoveries', {}).items():
            ids['disc'].add(r['i'])
        for k, r in rv.get('blackmarketVendors', {}).items():
            for ik, it in r.get('vendorItems', {}).items():
                if isinstance(it, dict):
                    vend_shapes[tuple(sorted(str(x) for x in it))] += 1
                    for f in ('itemID', 'i', 'id', 'itemId'):
                        if isinstance(it.get(f), int):
                            ids['vendor'].add(it[f])
                    for v in it.values():
                        if isinstance(v, str):
                            for m in HIT.findall(v):
                                ids['vendor'].add(int(m))
    for k in g.get('newWorldforgedItems', {}):
        ids['newWF'].add(k)
    for k in g.get('scannerData', {}):
        m = HIT.search(k)
        if m:
            ids['scanner'].add(int(m.group(1)))
print({k: len(v) for k, v in ids.items()})
print('vendorItems entry key-sets:', vend_shapes.most_common(5))
want = set().union(*ids.values())
zf = zipfile.ZipFile(r"D:\ascension data till 10-9 11 am\ascension-harvest-export.zip")
N = 'ascension-harvest-export/client-cache/dawnrise-dated-snapshots/itemcache-dawnrise-2026-09-01c.tsv'
rows = {}
total = 0
with zf.open(N) as fh:
    tf = io.TextIOWrapper(fh, encoding='utf-8', errors='replace', newline='')
    hdr = tf.readline().rstrip('\r\n').split('\t')
    for line in tf:
        total += 1
        t = line.rstrip('\r\n').split('\t')
        try:
            iid = int(t[0])
        except ValueError:
            continue
        if iid in want:
            rows[iid] = dict(zip(hdr[:12], t[:12]))
print('tsv rows', total, 'header', hdr[:12])
print('matched', len(rows), 'of', len(want))
pickle.dump(dict(ids={k: sorted(v) for k, v in ids.items()}, tsv=rows, tsv_name=N, tsv_total=total), open(OUT, 'wb'))
