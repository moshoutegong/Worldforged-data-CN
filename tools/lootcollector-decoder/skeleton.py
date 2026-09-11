"""Print a SANITIZED schema of every LootCollector SV: key shapes only, never string values."""
import sys, re, pickle, collections
sys.path.insert(0, r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc")
from common import lc_members
from luasv import parse_sv

OUT = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\parsed.pkl"

SAFE_KEY = re.compile(r'^[a-z][A-Za-z0-9_]{0,24}$')


def shape(k):
    if isinstance(k, bool):
        return 'bool'
    if isinstance(k, int):
        return 'int'
    if isinstance(k, float):
        return 'float'
    if isinstance(k, str):
        if SAFE_KEY.match(k):
            return k  # lowercase identifier-like config/record keys
        s = re.sub(r'[A-Za-z]', 'a', k)
        s = re.sub(r'[0-9]', '9', s)
        s = re.sub(r'a+', 'A', s)
        s = re.sub(r'9+', 'N', s)
        return '<' + s[:40] + '>'
    return type(k).__name__


def vt(v):
    if isinstance(v, dict):
        return 'table'
    if isinstance(v, str):
        return 'str'
    return type(v).__name__


def walk(d, path, depth, agg):
    if depth > 7:
        return
    for k, v in d.items():
        p = path + '/' + shape(k)
        agg[p][vt(v)] += 1
        if isinstance(v, dict):
            walk(v, p, depth + 1, agg)


allp = {}
for z, p, ai, sz, b in lc_members():
    text = b.decode('utf-8', 'replace')
    sv = parse_sv(text)
    allp[(z, p)] = sv
    agg = collections.defaultdict(collections.Counter)
    walk(sv, '', 0, agg)
    print('=====', z, p, 'top vars:', [shape(k) for k in sv])
    for path in sorted(agg):
        c = agg[path]
        print('  %-90s %s' % (path, dict(c)))
pickle.dump(allp, open(OUT, 'wb'))
