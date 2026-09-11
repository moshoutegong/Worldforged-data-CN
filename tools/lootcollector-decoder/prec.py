import pickle, collections
PK = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\parsed.pkl"
allp = pickle.load(open(PK, 'rb'))
recs = []
for (z, p), sv in allp.items():
    for rk, rv in sv['LootCollectorDB_Asc']['global'].get('realms', {}).items():
        for k, r in rv.get('discoveries', {}).items():
            recs.append((z, p, rk, k, r))
c = collections.Counter()
for *_, k, r in recs:
    x, y = k.split('-')[4:6]
    c['x==round4'] += abs(float(x) - round(r['xy']['x'], 4)) < 1e-9
    c['y==round4'] += abs(float(y) - round(r['xy']['y'], 4)) < 1e-9
    c['xy.x decimals<=4'] += len(repr(r['xy']['x']).split('.')[-1]) <= 4
print(len(recs), dict(c))
print('_lz x z:', collections.Counter((r['_lz'], r['z'], r.get('_rawZ')) for *_, r in recs if '_lz' in r).most_common(10))
print('realm x c:', sorted(collections.Counter((rk, r['c']) for _, _, rk, k, r in recs).items()))
