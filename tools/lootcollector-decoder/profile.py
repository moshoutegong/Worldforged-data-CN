"""Sanitized profile: collapsed schema + per-field value shapes. Never prints name-like string values."""
import sys, re, pickle, collections
PK = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\parsed.pkl"
allp = pickle.load(open(PK, 'rb'))
SAFE_KEY = re.compile(r'^[a-z][A-Za-z0-9_]{0,30}$')


def shp(s):
    s = re.sub(r'[A-Za-z]', 'a', s)
    s = re.sub(r'[0-9]', '9', s)
    s = re.sub(r'a+', 'A', s)
    s = re.sub(r'9+', 'N', s)
    return s[:50]


def kshape(k, parent):
    if isinstance(k, bool): return 'bool'
    if isinstance(k, int): return 'int'
    if isinstance(k, float): return 'float'
    if parent in ('char',): return '<CHARKEY>'
    if parent in ('realms',): return '<REALM>'
    if SAFE_KEY.match(k): return k
    return '<' + shp(k) + '>'


def vt(v):
    return 'table' if isinstance(v, dict) else ('str' if isinstance(v, str) else type(v).__name__)


def walk(d, path, parent, agg, depth=0):
    if depth > 8: return
    for k, v in d.items():
        ks = kshape(k, parent)
        p = path + '/' + ks
        agg[p][vt(v)] += 1
        if isinstance(v, dict):
            walk(v, p, k if isinstance(k, str) else '', agg, depth + 1)


print('#### top-level vars')
for (z, p), sv in allp.items():
    print(z, p, list(sv.keys()))
    for top, db in sv.items():
        print('   top keys:', [kshape(k, '') for k in db])
        g = db.get('global', {})
        print('   global keys:', sorted(kshape(k, 'global') for k in g))
        for rk, rv in g.get('realms', {}).items():
            print('   REALM %r :' % rk, {k: (len(v) if isinstance(v, dict) else vt(v)) for k, v in rv.items()})
        print('   n char entries:', len(db.get('char', {})))

print('\n#### collapsed schema (union), counts per file')
aggs = {}
for fk, sv in allp.items():
    agg = collections.defaultdict(collections.Counter)
    walk(sv, '', '', agg)
    aggs[fk] = agg
paths = sorted(set().union(*[set(a) for a in aggs.values()]))
for p in paths:
    if '/char/' in p and '/mapFilters/' in p: continue
    print('  %-95s' % p[:95], ' | '.join(str(dict(aggs[f].get(p, {}))) for f in aggs))
