"""Load NPC/GO spawn coords from the dump's dumps_part*.zip (+ Bronzebeard CSV) and validate the
world-map -> server formula on records that carry BOTH MapX/MapY and internal X/Y."""
import zipfile, re, os, pickle, collections, statistics
D = r"D:\ascension data till 10-9 11 am"
L = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc"
wma = pickle.load(open(L + r"\wma.pkl", 'rb'))
REC = re.compile(r'\{([^{}]*)\}')
KV = re.compile(r'"?([A-Za-z][A-Za-z _]*?)"?\s*:\s*("(?:\\.|[^"\\])*"|[-0-9.eE]+)')
pts = []  # (kind, id, map, x, y, z, mapname, mapx, mapy)
for zn in ('dumps-part1.zip', 'dumps_part2.zip', 'dumps_part3.zip', 'dumps_part4.zip'):
    zf = zipfile.ZipFile(os.path.join(D, zn))
    for n in zf.namelist():
        b = os.path.basename(n)
        if not b.endswith('.txt'):
            continue
        kind = 'npc' if b.startswith('dump_npc_') else 'go'
        t = zf.read(n).decode('utf-8', 'replace')
        for m in REC.finditer(t):
            d = {}
            for k, v in KV.findall(m.group(1)):
                d[k.strip()] = v[1:-1] if v.startswith('"') else float(v)
            try:
                pts.append((kind, int(d['id']), int(d['internal map id']), d['internal X'], d['internal Y'], d['internal Z'],
                            d.get('Map internal name'), d.get('MapX'), d.get('MapY')))
            except (KeyError, ValueError):
                pass
zf = zipfile.ZipFile(os.path.join(D, 'GameObjects-Bronzebeard.zip'))
for n in zf.namelist():
    if not n.endswith('.csv'):
        continue
    lines = zf.read(n).decode('utf-8', 'replace').splitlines()
    for ln in lines[1:]:
        c = [s.strip().strip('"') for s in ln.split(';')]
        if len(c) < 11:
            continue
        try:
            f = lambda s: float(s.replace(',', '.'))
            pts.append(('gobb', int(c[0]), int(c[7]), f(c[8]), f(c[9]), f(c[10]), c[4], f(c[5]), f(c[6])))
        except ValueError:
            pass
print('spawn points', collections.Counter(p[0] for p in pts))
# formula validation. Our formula: X = T - (MapY/100)*(T-B) ; Y = L - (MapX/100)*(L-R)
byname = {}
for r in wma['captured'].values():
    byname.setdefault(r['name'], r)
unk = collections.Counter()
bysrc = collections.defaultdict(list)
expq = collections.defaultdict(list)
out_of_zone = collections.Counter()
for kind, i, mp, x, y, zz, nm, mx, my in pts:
    w = byname.get(nm)
    if not w or mx is None:
        unk[nm] += 1
        continue
    if not (0 <= mx <= 100 and 0 <= my <= 100):
        out_of_zone[kind] += 1
        continue
    if w['map'] != mp:
        out_of_zone[kind + '-mapmismatch'] += 1
        continue
    X = w['T'] - (my / 100.0) * (w['T'] - w['B'])
    Y = w['L'] - (mx / 100.0) * (w['L'] - w['R'])
    bysrc[kind].append(((X - x) ** 2 + (Y - y) ** 2) ** 0.5)
    # expected error from 1-dp MapX/MapY rounding: uniform +-0.05% per axis -> RMS radius
    ex = 0.0005 * abs(w['T'] - w['B']) / 3 ** 0.5
    ey = 0.0005 * abs(w['L'] - w['R']) / 3 ** 0.5
    expq[kind].append((ex * ex + ey * ey) ** 0.5)
print('unmatched map names (count)', sum(unk.values()), 'distinct', len(unk), '| skipped', dict(out_of_zone))
for kind, err in bysrc.items():
    err.sort()
    q = lambda f: err[int(f * (len(err) - 1))]
    e2 = sorted(expq[kind])
    print('%-5s n=%d position error yd: median %.2f p90 %.2f p99 %.2f max %.1f | <=1yd %d <=5yd %d | expected RMS from 1-dp rounding median %.2f' % (
        kind, len(err), q(.5), q(.9), q(.99), err[-1], sum(e <= 1 for e in err), sum(e <= 5 for e in err), e2[len(e2) // 2]))
print('MapX sample range', min(p[7] for p in pts if p[7] is not None), max(p[7] for p in pts if p[7] is not None))
pickle.dump(pts, open(L + r"\spawns.pkl", 'wb'))
