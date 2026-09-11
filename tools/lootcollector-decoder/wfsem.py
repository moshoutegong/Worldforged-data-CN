"""What do dt / isWF / newWorldforgedItems mean? Item names are game data."""
import pickle, re, collections
L = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc"
allp = pickle.load(open(L + r"\parsed.pkl", 'rb'))
items = pickle.load(open(L + r"\items.pkl", 'rb'))
tsv = items['tsv']
HIT = re.compile(r'Hitem:(\d+)')
NAME = re.compile(r'\|h\[(.*?)\]\|h')
scan = {}
newwf = set()
for (z, p), sv in allp.items():
    g = sv['LootCollectorDB_Asc']['global']
    newwf |= set(g.get('newWorldforgedItems', {}))
    for k, v in g.get('scannerData', {}).items():
        m = HIT.search(k)
        if m and isinstance(v, dict):
            scan.setdefault(int(m.group(1)), set()).add(bool(v.get('isWF')))
recs = {}
for (z, p), sv in allp.items():
    for rk, rv in sv['LootCollectorDB_Asc']['global'].get('realms', {}).items():
        for k, r in rv.get('discoveries', {}).items():
            recs[(rk, k)] = r
byi = {}
for r in recs.values():
    byi.setdefault(r['i'], r)
print('scanner items', len(scan), 'isWF true', sum(1 for v in scan.values() if True in v), 'mixed', sum(1 for v in scan.values() if len(v) > 1))
for dt in (1, 2, 4):
    its = {r['i'] for r in recs.values() if r['dt'] == dt}
    wf = sum(1 for i in its if True in scan.get(i, ()))
    nwf = sum(1 for i in its if False in scan.get(i, ()) and True not in scan.get(i, ()))
    print('dt', dt, 'items', len(its), 'scanner isWF=T', wf, 'scanner isWF=F', nwf, 'not scanned', len(its) - wf - nwf,
          'in newWorldforgedItems', len(its & newwf), 'in tsv', len(its & set(tsv)))
    samp = sorted(its)[:: max(1, len(its) // 12)][:12]
    print('   sample names:', [(i, NAME.search(byi[i]['il']).group(1) if NAME.search(byi[i]['il']) else None) for i in samp])
print('newWF ids', len(newwf), 'in disc', len(newwf & set(byi)), 'scanner WF true ids not in disc', len({i for i, v in scan.items() if True in v} - set(byi)))
# name pattern for dt1
c = collections.Counter()
for i, r in byi.items():
    m = NAME.search(r['il'])
    nm = m.group(1) if m else ''
    c[(r['dt'], 'Mystic Scroll' in nm or nm.startswith('Scroll'), 'Worldforged' in nm)] += 1
print(c)
# item-link colour vs q
print('link colour x q', collections.Counter((r['il'][2:10], r['q']) for r in byi.values()).most_common(12))
# ilvl from tsv for dt1
lv = collections.Counter()
for i, r in byi.items():
    if i in tsv:
        lv[(r['dt'], tsv[i]['class'])] += 1
print('dt x tsv class', sorted(lv.items()))
