"""LootCollector lens: dedupe, WF, item join, zone distribution, server-coordinate conversion,
nearest-spawn check. PRIVACY: never reads out fp / o / fp_votes / ack_votes / _ln / aoeTombstones.name
/ vendorName / char keys VALUES -- only counts."""
import pickle, re, collections, json, datetime, math, csv
L = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc"
DES = r"D:\acore-classless\build\design"
allp = pickle.load(open(L + r"\parsed.pkl", 'rb'))
items = pickle.load(open(L + r"\items.pkl", 'rb'))
wma = pickle.load(open(L + r"\wma.pkl", 'rb'))
pts = pickle.load(open(L + r"\spawns.pkl", 'rb'))
tsv = items['tsv']
cached = {int(x) for x in open(DES + r"\zones-item-ids.txt").read().replace('\n', ',').split(',') if x.strip()}
live = {int(x) for x in open(DES + r"\zones-live-itemids.txt").read().split() if x.strip().isdigit()}
cap, stock = wma['captured'], wma['stock']
HIT = re.compile(r'Hitem:(\d+)')
NAME = re.compile(r'\|h\[(.*?)\]\|h')
ACCT = {'Account.zip': 'A0', 'Account (1).zip': 'A1', 'Account (2).zip': 'A2'}
out = collections.OrderedDict()


def P(*a):
    print(*a)


def ts(t):
    return datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d')


# ---------------- load ----------------
rows = []      # (acct, file, realm, key, rec)
scan = {}
newwf = set()
priv = collections.Counter()
privsets = collections.defaultdict(set)
vendors = []
for (z, p), sv in allp.items():
    acct = ACCT[z]
    fn = 'bak' if p.endswith('.bak') else 'lua'
    db = sv['LootCollectorDB_Asc']
    priv['char entries (Char - Realm keys)'] += len(db.get('char', {}))
    priv['profileKeys entries'] += len(db.get('profileKeys', {}))
    for ck, cv in db.get('char', {}).items():
        priv['char.looted entries'] += len(cv.get('looted', {}))
    g = db['global']
    newwf |= set(g.get('newWorldforgedItems', {}))
    for t in g.get('aoeTombstones', {}).values():
        if isinstance(t, dict) and 'name' in t:
            priv['aoeTombstones.name'] += 1
    for k, v in g.get('scannerData', {}).items():
        m = HIT.search(k)
        if m and isinstance(v, dict):
            scan.setdefault(int(m.group(1)), set()).add(bool(v.get('isWF')))
    for rk, rv in g.get('realms', {}).items():
        for k, r in rv.get('discoveries', {}).items():
            rows.append((acct, fn, rk, k, r))
            for f in ('fp', 'o', '_ln'):
                if f in r:
                    priv['discoveries.' + f] += 1
                    privsets[f].add(r[f])
            for f in ('fp_votes', 'ack_votes'):
                if isinstance(r.get(f), dict):
                    priv['discoveries.%s keys' % f] += len(r[f])
                    privsets[f] |= set(r[f])
        for k, r in rv.get('blackmarketVendors', {}).items():
            vendors.append((acct, fn, rk, k, r))
            if 'vendorName' in r:
                priv['blackmarketVendors.vendorName'] += 1
                privsets['vendorName'].add(r['vendorName'])
            for f in ('fp', 'o'):
                if f in r:
                    priv['blackmarketVendors.' + f] += 1
                    privsets['bm_' + f].add(r[f])
out['privacy_counts'] = dict(priv)
out['privacy_distinct'] = {k: len(v) for k, v in privsets.items()}
P('PRIVACY field counts (values never printed):', dict(priv))
P('PRIVACY distinct-value counts:', {k: len(v) for k, v in privsets.items()})

# ---------------- counts ----------------
P('\n## raw records per file')
for a in ('A0', 'A1', 'A2'):
    for fn in ('lua', 'bak'):
        rr = [x for x in rows if x[0] == a and x[1] == fn]
        P(a, fn, len(rr), dict(collections.Counter(x[2] for x in rr)))
P('raw discovery records total', len(rows), '| blackmarket vendor records total', len(vendors))

# dedupe
by_rk = {}
for a, fn, rk, k, r in rows:
    by_rk.setdefault((rk, k), []).append((a, fn, r))
by_k = {}
for (rk, k), lst in by_rk.items():
    by_k.setdefault(k, []).append((rk, lst))
P('\ndistinct (realm,key)', len(by_rk), '| distinct key (cross-realm)', len(by_k))
lua_only = {(rk, k) for a, fn, rk, k, r in rows if fn == 'lua'}
P('distinct (realm,key) from .lua files only', len(lua_only), '| added by .bak files', len(by_rk) - len(lua_only))
accts_per = collections.Counter(len({a for a, fn, r in lst}) for lst in by_rk.values())
P('(realm,key) seen in N accounts', sorted(accts_per.items()))
realms_per = collections.Counter(len(v) for v in by_k.values())
P('key seen on N realms', sorted(realms_per.items()))
P('distinct (realm,key) per realm', sorted(collections.Counter(rk for rk, k in by_rk).items()))


def best(lst):
    # prefer .lua over .bak, then latest ls
    return sorted(lst, key=lambda t: (t[1] == 'lua', t[2].get('ls', 0)))[-1][2]


uniq = {rk_k: best(lst) for rk_k, lst in by_rk.items()}
recs = list(uniq.values())
items_all = {r['i'] for r in recs}
P('distinct item ids', len(items_all))
loc4 = {(r['i'], r['z'], k.split('-')[4], k.split('-')[5]) for (rk, k), r in uniq.items()}
P('distinct (item, z, x4, y4) locations', len(loc4))
loc2 = {(r['i'], r['z'], round(r['xy']['x'], 2), round(r['xy']['y'], 2)) for r in recs}
P('distinct (item, z, x2, y2) locations (~1% map grid)', len(loc2))
spot = {(r['z'], k.split('-')[4], k.split('-')[5]) for (rk, k), r in uniq.items()}
P('distinct (z, x4, y4) spots ignoring item', len(spot))
P('dt counts (dedup)', sorted(collections.Counter(r['dt'] for r in recs).items()))
P('status s (dedup)', collections.Counter(r['s'] for r in recs).most_common())
P('t0 range', ts(min(r['t0'] for r in recs)), '->', ts(max(r['t0'] for r in recs)), '| ls max', ts(max(r['ls'] for r in recs)))

# ---------------- WF ----------------
def isWF_scan(i):
    return True in scan.get(i, ())


wf_recs = [r for r in recs if r['dt'] == 1]
wf_items = {r['i'] for r in wf_recs}
P('\n## WF: dt==1 records', len(wf_recs), 'items', len(wf_items), '| scanner isWF=true', sum(isWF_scan(i) for i in wf_items),
  '| in newWorldforgedItems', len(wf_items & newwf))
P('dt==2 (Mystic Scroll) records', sum(r['dt'] == 2 for r in recs), 'items', len({r['i'] for r in recs if r['dt'] == 2}))
P('dt==4 records', sum(r['dt'] == 4 for r in recs), 'items', len({r['i'] for r in recs if r['dt'] == 4}))
scanWF = {i for i, v in scan.items() if True in v}
P('scanner isWF=true items total', len(scanWF), '| of those with a location', len(scanWF & items_all),
  '| newWorldforgedItems ids', len(newwf), 'with location', len(newwf & items_all))
# ilvl
ilv = collections.Counter()
qc = collections.Counter()
cls = collections.Counter()
inv = collections.Counter()
nm_by_i = {}
for r in recs:
    m = NAME.search(r['il'])
    nm_by_i.setdefault(r['i'], m.group(1) if m else '')
for i in wf_items:
    t = tsv.get(i)
    if t:
        il = int(t['itemLevel'])
        ilv[(il // 10) * 10] += 1
        qc[t['quality']] += 1
        cls[(t['class'], t['subclass'])] += 1
        inv[t['invType']] += 1
P('WF items with tsv row', sum(1 for i in wf_items if i in tsv))
P('WF ilvl buckets', sorted(ilv.items()))
P('WF tsv quality', sorted(qc.items()))
P('WF tsv invType', sorted(inv.items(), key=lambda t: int(t[0])))
ilvals = sorted(int(tsv[i]['itemLevel']) for i in wf_items if i in tsv)
rq = sorted(int(tsv[i]['reqLevel']) for i in wf_items if i in tsv)
P('WF ilvl min/median/max', ilvals[0], ilvals[len(ilvals) // 2], ilvals[-1], '| reqLevel min/median/max', rq[0], rq[len(rq) // 2], rq[-1])
# id bands
band = collections.Counter()
for i in wf_items:
    band['%dxxxxx' % (i // 100000)] += 1
P('WF item id bands (i // 100000)', sorted(band.items(), key=lambda t: int(t[0][:-5])))
# joins
for tag, S in (('all', items_all), ('WF', wf_items)):
    P('JOIN %s: n=%d  in cached 55,454 set %d | in our Ascension-only (cached-live) %d | in live item_template %d | in harvest itemcache tsv %d | in none %d' % (
        tag, len(S), len(S & cached), len((S & cached) - live), len(S & live), len(S & set(tsv)),
        len(S - cached - live - set(tsv))))
not_tsv = sorted(wf_items - set(tsv))
P('WF items missing from tsv:', not_tsv)

# ---------------- zones ----------------
P('\n## zone distribution (dedup records, WF only). z -> WMA.dbc ID z-1')
zc = collections.Counter(r['z'] for r in wf_recs)
zi = collections.defaultdict(set)
for r in wf_recs:
    zi[r['z']].add(r['i'])
unmapped = collections.Counter()
mapc = collections.Counter()
zone_rows = []
for z, n in zc.most_common():
    w = cap.get(z - 1)
    if not w:
        unmapped[z] += n
        continue
    mapc[w['map']] += n
    zone_rows.append((z, z - 1, w['name'], w['map'], w['area'], n, len(zi[z]), z - 1 in stock))
P('z values', len(zc), '| unmapped z (no WMA row at z-1):', dict(unmapped))
P('records by server map', mapc.most_common())
for zr in zone_rows:
    P('  z=%d wma=%d %-28s map=%d area=%d recs=%d items=%d stockWMA=%s' % zr)
out['zone_rows'] = zone_rows
P('c (continent) x server map of WMA(z-1):', sorted(collections.Counter((r['c'], cap[r['z'] - 1]['map'] if (r['z'] - 1) in cap else None) for r in recs).items(), key=str))
P('Pale Reach (z=2063 / WMA 2062) records:', sum(r['z'] == 2063 for r in recs), '| z=2022 WMA 2021:', cap.get(2021))


# ---------------- conversion ----------------
def conv(r, x, y, table=cap):
    w = table.get(r['z'] - 1)
    if not w:
        return None
    X = w['T'] - y * (w['T'] - w['B'])
    Y = w['L'] - x * (w['L'] - w['R'])
    return w['map'], X, Y, (w['T'] - w['B']), (w['L'] - w['R'])


res1 = []
for r in recs:
    c = conv(r, r['xy']['x'], r['xy']['y'])
    if c:
        res1.append(max(c[3], c[4]) * 1e-4 / 2)
res1.sort()
P('\nquantisation half-step (yd) for 4-dp coords: median %.3f max %.3f' % (res1[len(res1) // 2], res1[-1]))
# captured vs stock bounds: systematic offset if we used stock bounds
d = []
for r in recs:
    a = conv(r, r['xy']['x'], r['xy']['y'], cap)
    b = conv(r, r['xy']['x'], r['xy']['y'], stock)
    if a and b:
        d.append(math.hypot(a[1] - b[1], a[2] - b[2]))
d.sort()
P('captured(Ascension) vs stock WMA bounds shift, same x/y: n=%d median %.2f p99 %.2f max %.2f yd' % (len(d), d[len(d) // 2], d[int(.99 * (len(d) - 1))], d[-1]))
# key xy vs stored xy
dk = []
for (rk, k), r in uniq.items():
    kx, ky = float(k.split('-')[4]), float(k.split('-')[5])
    a = conv(r, kx, ky)
    b = conv(r, r['xy']['x'], r['xy']['y'])
    if a and b:
        dk.append(math.hypot(a[1] - b[1], a[2] - b[2]))
dk.sort()
P('key-xy vs stored xy: n=%d identical %d median %.2f p90 %.2f p99 %.2f max %.1f yd' % (
    len(dk), sum(x < 1e-6 for x in dk), dk[len(dk) // 2], dk[int(.9 * (len(dk) - 1))], dk[int(.99 * (len(dk) - 1))], dk[-1]))

# ---------------- nearest spawn ----------------
grid = collections.defaultdict(list)
CS = 50.0
for kind, i, mp, x, y, zz, nm, mx, my in pts:
    grid[(mp, int(x // CS), int(y // CS))].append((kind, i, x, y, zz))


def nearest(mp, X, Y, kinds):
    bestd, bestp = 1e9, None
    for ring in range(0, 6):
        for gx in range(int(X // CS) - ring, int(X // CS) + ring + 1):
            for gy in range(int(Y // CS) - ring, int(Y // CS) + ring + 1):
                if max(abs(gx - int(X // CS)), abs(gy - int(Y // CS))) != ring:
                    continue
                for p in grid.get((mp, gx, gy), ()):
                    if p[0] in kinds:
                        dd = math.hypot(p[2] - X, p[3] - Y)
                        if dd < bestd:
                            bestd, bestp = dd, p
        if bestp and bestd <= ring * CS:
            break
    return bestd, bestp


# aggregate WF locations (cross-realm dedupe on (item,z,x4,y4))
agg = {}
for (rk, k), r in uniq.items():
    if r['dt'] != 1:
        continue
    kx, ky = k.split('-')[4], k.split('-')[5]
    key = (r['i'], r['z'], kx, ky)
    a = agg.setdefault(key, dict(realms=set(), recs=0, xs=[], ys=[], r=r))
    a['realms'].add(rk)
    a['recs'] += 1
    a['xs'].append(r['xy']['x'])
    a['ys'].append(r['xy']['y'])
P('\nWF unique (item,z,x4,y4):', len(agg))
dgo, dnpc = [], []
csvrows = []
maps_with_spawns = {p[2] for p in pts}
for (i, z, kx, ky), a in sorted(agg.items()):
    r = a['r']
    x = sum(a['xs']) / len(a['xs'])
    y = sum(a['ys']) / len(a['ys'])
    c = conv(r, x, y)
    if not c:
        continue
    mp, X, Y = c[0], c[1], c[2]
    ng = nearest(mp, X, Y, ('go', 'gobb'))
    nn = nearest(mp, X, Y, ('npc',))
    if ng[1]:
        dgo.append(ng[0])
    if nn[1]:
        dnpc.append(nn[0])
    t = tsv.get(i, {})
    w = cap[z - 1]
    csvrows.append([i, nm_by_i.get(i, ''), t.get('itemLevel', ''), t.get('reqLevel', ''), r['q'], z, z - 1, w['name'], mp,
                    '%.4f' % x, '%.4f' % y, '%.1f' % X, '%.1f' % Y,
                    ng[1][1] if ng[1] else '', '%.1f' % ng[0] if ng[1] else '', ng[1][4] if ng[1] else '',
                    len(a['realms']), a['recs']])


def pct(v, f):
    return v[int(f * (len(v) - 1))] if v else float('nan')


for tag, v in (('GO', dgo), ('NPC', dnpc)):
    v.sort()
    P('nearest dump %s spawn (same map, 2D) for WF locations: n=%d median %.1f p25 %.1f p75 %.1f p90 %.1f | <=3yd %d <=5yd %d <=10yd %d <=25yd %d' % (
        tag, len(v), pct(v, .5), pct(v, .25), pct(v, .75), pct(v, .9), sum(x <= 3 for x in v), sum(x <= 5 for x in v), sum(x <= 10 for x in v), sum(x <= 25 for x in v)))
P('WF locations on maps with any dump spawn:', sum(1 for row in csvrows if row[8] in maps_with_spawns), 'of', len(csvrows))
# which GO entries are nearest within 5yd (object ids are game data)
gohits = collections.Counter(row[13] for row in csvrows if row[14] and float(row[14]) <= 5)
P('GO ids nearest (<=5yd) top 15:', gohits.most_common(15))
with open(L + r"\wf_locations.csv", 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['item_id', 'item_name', 'item_level', 'req_level', 'quality', 'lc_z_mapAreaId', 'wma_id', 'wma_name', 'server_map',
                'norm_x', 'norm_y', 'server_X', 'server_Y', 'nearest_dump_go_entry', 'nearest_go_dist_yd', 'nearest_go_z',
                'n_realms', 'n_records'])
    w.writerows(csvrows)
P('csv rows', len(csvrows))
pickle.dump(dict(uniq=uniq, agg=agg, csvrows=csvrows), open(L + r"\main.pkl", 'wb'))
