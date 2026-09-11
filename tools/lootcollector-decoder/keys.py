"""Composite-key decomposition + safe categorical fields (non-person enums only)."""
import sys, re, pickle, collections
PK = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\parsed.pkl"
allp = pickle.load(open(PK, 'rb'))
recs = []
for (z, p), sv in allp.items():
    db = sv['LootCollectorDB_Asc']
    for rk, rv in db['global'].get('realms', {}).items():
        for k, r in rv.get('discoveries', {}).items():
            recs.append((z, p, rk, k, r))

# enums that are not person names (<=25 distinct values over thousands of rows)
for f in ('cl', 's', 'src', 'el', 'av', '_lz'):
    c = collections.Counter(r.get(f) for *_, r in recs if isinstance(r.get(f), str))
    assert len(c) <= 25, f
    print(f, sorted(c.items(), key=lambda t: -t[1]))

# key vs fields
agree = collections.Counter()
n = 0
bad = 0
for z, p, rk, k, r in recs:
    parts = k.split('-')
    if len(parts) != 6:
        bad += 1
        continue
    n += 1
    a, b, c_, item, x, y = parts
    agree['key==g'] += (k == r.get('g'))
    agree['a==c'] += (int(a) == r.get('c'))
    agree['b==z'] += (int(b) == r.get('z'))
    agree['c==iz'] += (int(c_) == r.get('iz'))
    agree['item==i'] += (int(item) == r.get('i'))
    xx, yy = r['xy']['x'], r['xy']['y']
    agree['x==round(xy.x,2)'] += (abs(float(x) - round(xx, 2)) < 1e-9)
    agree['y==round(xy.y,2)'] += (abs(float(y) - round(yy, 2)) < 1e-9)
    agree['x==trunc'] += (abs(float(x) - int(xx * 100) / 100) < 1e-9)
    agree['xdec'] += len(x.split('.')[-1]) if '.' in x else 0
print('keys parsed', n, 'bad', bad)
print(dict(agree))
xs = collections.Counter(len(k.split('-')[4].split('.')[-1]) for *_, k, r in recs if len(k.split('-')) == 6)
print('x decimals', xs)
print('xy.x range', min(r['xy']['x'] for *_, r in recs), max(r['xy']['x'] for *_, r in recs))
print('xy.y range', min(r['xy']['y'] for *_, r in recs), max(r['xy']['y'] for *_, r in recs))
# c vs z consistency
cz = collections.defaultdict(collections.Counter)
for *_, r in recs:
    cz[r['z']][r['c']] += 1
multi = {z: dict(v) for z, v in cz.items() if len(v) > 1}
print('zones with >1 c value:', multi)
print('c by count of zones:', collections.Counter(max(v, key=v.get) for v in cz.values()))
# _rawZ vs z
rz = collections.Counter((r['_rawZ'], r['z']) for *_, r in recs if '_rawZ' in r)
print('_rawZ->z pairs (top 30):', rz.most_common(30))
# dt x q x it
print('dt x it', collections.Counter((r['dt'], r['it']) for *_, r in recs).most_common(20))
print('dt x q', sorted(collections.Counter((r['dt'], r['q']) for *_, r in recs).items()))
print('dt x src', collections.Counter((r['dt'], r.get('src')) for *_, r in recs).most_common(20))
print('iz!=0 zones', collections.Counter((r['c'], r['z'], r['iz']) for *_, r in recs if r['iz']))
