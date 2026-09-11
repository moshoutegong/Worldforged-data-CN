"""Characterise the dump gameobjects nearest the WF pins (GO names/types are game data) and
overlap with the installed addon's WorldforgedList."""
import zipfile, re, os, pickle, json, collections, csv
D = r"D:\ascension data till 10-9 11 am"
L = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc"
m = pickle.load(open(L + r"\main.pkl", 'rb'))
rows = m['csvrows']
# GO names/types from dumps (dump_<Zone>.txt: Name, LockID, LockType) and Bronzebeard CSV (Name, Type)
REC = re.compile(r'\{([^{}]*)\}')
KV = re.compile(r'"?([A-Za-z][A-Za-z _]*?)"?\s*:\s*("(?:\\.|[^"\\])*"|[-0-9.eE]+)')
gname, gtype = {}, {}
for zn in ('dumps-part1.zip', 'dumps_part2.zip', 'dumps_part3.zip', 'dumps_part4.zip'):
    zf = zipfile.ZipFile(os.path.join(D, zn))
    for n in zf.namelist():
        b = os.path.basename(n)
        if not b.endswith('.txt') or b.startswith('dump_npc_'):
            continue
        for mo in REC.finditer(zf.read(n).decode('utf-8', 'replace')):
            d = {k.strip(): (v[1:-1] if v.startswith('"') else v) for k, v in KV.findall(mo.group(1))}
            if 'id' in d:
                i = int(float(d['id']))
                if d.get('Name'):
                    gname.setdefault(i, d['Name'])
                if d.get('LockType'):
                    gtype.setdefault(i, 'lock:' + d['LockType'])
zf = zipfile.ZipFile(os.path.join(D, 'GameObjects-Bronzebeard.zip'))
for n in zf.namelist():
    if n.endswith('.csv'):
        for ln in zf.read(n).decode('utf-8', 'replace').splitlines()[1:]:
            c = [s.strip().strip('"') for s in ln.split(';')]
            if len(c) >= 3 and c[0].isdigit():
                gname.setdefault(int(c[0]), c[1])
                gtype[int(c[0])] = 'type:' + c[2]
ids = json.load(open(r"D:\acore-classless\build\design\zones-extract\_union-ids.json", encoding='utf-8'))
asc = json.load(open(r"D:\acore-classless\build\design\zones-extract\_ascension-only-ids.json", encoding='utf-8'))
cached_go = set(ids['gameobject_ids'])
asc_go = set(asc['ascension_only_gameobjects'])
for lim in (3, 5, 10):
    hit = [r for r in rows if r[14] != '' and float(r[14]) <= lim]
    goset = {int(r[13]) for r in hit}
    print('<=%dyd: pins %d, distinct GO entries %d, in our GO template cache %d, Ascension-only %d' % (
        lim, len(hit), len(goset), len(goset & cached_go), len(goset & asc_go)))
hit = [r for r in rows if r[14] != '' and float(r[14]) <= 5]
tc = collections.Counter(gtype.get(int(r[13]), '?') for r in hit)
print('GO type/lock of <=5yd nearest:', tc.most_common(12))
nc = collections.Counter(gname.get(int(r[13]), '?') for r in hit)
print('GO names of <=5yd nearest (top 25):', nc.most_common(25))
bands = collections.Counter(int(r[13]) // 100000 for r in hit)
print('GO entry bands (//100000):', sorted(bands.items()))
# same GO entry nearest to many pins of the SAME item? (one spawn object per item?)
per = collections.defaultdict(set)
for r in hit:
    per[int(r[13])].add(r[0])
print('GO entries nearest (<=5yd) to exactly 1 distinct item: %d, to >1 items: %d' % (
    sum(1 for v in per.values() if len(v) == 1), sum(1 for v in per.values() if len(v) > 1)))
# installed addon WorldforgedList overlap (NOT dump data)
wl = {int(x) for x in re.findall(r'\b(\d{5,8})\b', open(r"D:\games\ascension-live\Interface\AddOns\LootCollector\Modules\WorldforgedList.lua", encoding='utf-8', errors='replace').read())}
wf_items = {r[0] for r in rows}
print('installed WorldforgedList ids', len(wl), '| dump WF items with a pin', len(wf_items), '| overlap', len(wl & wf_items),
      '| list ids with no pin in dump', len(wl - wf_items))
