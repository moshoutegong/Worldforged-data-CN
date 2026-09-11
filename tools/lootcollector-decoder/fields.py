"""Field value profile for discovery records. Name-risk string fields show SHAPE only."""
import sys, re, pickle, collections
PK = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\parsed.pkl"
allp = pickle.load(open(PK, 'rb'))


def shp(s):
    s = re.sub(r'[A-Za-z]', 'a', s)
    s = re.sub(r'[0-9]', '9', s)
    s = re.sub(r'a+', 'A', s)
    s = re.sub(r'9+', 'N', s)
    return s[:60]


NUMSTR = re.compile(r'^[-0-9:.,;|_ ]*$')
recs = []
for (z, p), sv in allp.items():
    db = sv['LootCollectorDB_Asc']
    for rk, rv in db['global'].get('realms', {}).items():
        for sect in ('discoveries', 'blackmarketVendors'):
            for k, r in rv.get(sect, {}).items():
                recs.append((z, p, rk, sect, k, r))
print('total records (all files, incl dupes):', len(recs))
fields = collections.defaultdict(list)
for z, p, rk, sect, k, r in recs:
    if sect != 'discoveries':
        continue
    for f, v in r.items():
        fields[f].append(v)
for f in sorted(fields, key=str):
    vals = fields[f]
    types = collections.Counter(type(v).__name__ for v in vals)
    line = '%-16r n=%-6d types=%s' % (f, len(vals), dict(types))
    nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
    strs = [v for v in vals if isinstance(v, str)]
    if nums:
        c = collections.Counter(nums)
        line += ' | num min=%s max=%s distinct=%d' % (min(nums), max(nums), len(c))
        if len(c) <= 40:
            line += ' vals=%s' % sorted(c.items())
        else:
            line += ' top=%s' % c.most_common(8)
    if strs:
        allnum = all(NUMSTR.match(s) for s in strs)
        if allnum and f not in ('fp', 'o', 'g', 'cl', 'av', 'el'):
            c = collections.Counter(strs)
            line += ' | numeric-str distinct=%d top=%s' % (len(c), c.most_common(12))
        else:
            c = collections.Counter(shp(s) for s in strs)
            line += ' | str distinct_values=%d shapes(top)=%s' % (len(set(strs)), c.most_common(6))
    tabs = [v for v in vals if isinstance(v, dict)]
    if tabs:
        kk = collections.Counter()
        for t in tabs:
            for kx in t:
                kk[kx if (isinstance(kx, str) and re.match(r'^[a-z]{1,6}$', kx)) else '<' + shp(str(kx)) + '>'] += 1
        line += ' | table keys=%s' % kk.most_common(8)
    print(line)
