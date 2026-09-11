"""Ground truth: LootCollector CoordAuthority rows are maintainer 'stand on the spawn' coords.
Compare dump LC records for those (item, z) to the authority xy, in yards via the WMA conversion."""
import pickle, math, re
L = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc"
m = pickle.load(open(L + r"\main.pkl", 'rb'))
wma = pickle.load(open(L + r"\wma.pkl", 'rb'))
pts = pickle.load(open(L + r"\spawns.pkl", 'rb'))
cap = wma['captured']
src = open(r"D:\games\ascension-live\Interface\AddOns\LootCollector\Modules\CoordAuthority.lua", encoding='utf-8', errors='replace').read()
AUTH = re.findall(r'\[(\d+)\]\s*=\s*\{\s*\[(\d+)\]\s*=\s*\{\s*c\s*=\s*(\d+),\s*x\s*=\s*([0-9.]+),\s*y\s*=\s*([0-9.]+)', src)
print('authority rows', len(AUTH))


def conv(z, x, y):
    w = cap[z - 1]
    return w['map'], w['T'] - y * (w['T'] - w['B']), w['L'] - x * (w['L'] - w['R'])


allm = []
for i, z, c, x, y in AUTH:
    i, z, x, y = int(i), int(z), float(x), float(y)
    mp, AX, AY = conv(z, x, y)
    ds = []
    for (rk, k), r in m['uniq'].items():
        if r['i'] == i and r['z'] == z:
            _, X, Y = conv(z, r['xy']['x'], r['xy']['y'])
            ds.append(math.hypot(X - AX, Y - AY))
    # nearest dump GO to the authority point
    best = min(((math.hypot(p[3] - AX, p[4] - AY), p[1]) for p in pts if p[2] == mp and p[0] in ('go', 'gobb')), default=(None, None))
    allm += ds
    print('item %d z=%d auth->server map %d (%.1f, %.1f) | LC recs %d dist yd %s | nearest dump GO %s at %.1f yd' % (
        i, z, mp, AX, AY, len(ds), sorted(round(d, 1) for d in ds)[:6], best[1], best[0] if best[0] is not None else -1))
allm.sort()
if allm:
    print('ALL LC-record vs authority distances n=%d median %.1f p90 %.1f max %.1f' % (len(allm), allm[len(allm) // 2], allm[int(.9 * (len(allm) - 1))], allm[-1]))
