"""Parse captured (== patch-M) WorldMapArea.dbc and Content/WorldMapAreaData.json; compare."""
import sys, struct, json, zipfile, pickle
sys.path.insert(0, r"D:\acore-classless\build\design")
from importlib import util
spec = util.spec_from_file_location('zdbc', r"D:\acore-classless\build\design\zones-dbc.py")
zdbc = util.module_from_spec(spec); spec.loader.exec_module(zdbc)
OUT = r"C:\Users\USER\AppData\Local\Temp\claude\C--CLAUDE\c1d4531f-f6e2-4f95-9dca-17d7cefc226a\scratchpad\lc\wma.pkl"

def f(u):
    return struct.unpack('<f', struct.pack('<I', u))[0]

res = {}
for tag, path in (('captured', r"D:\acore-classless\reference\captured\client\dbc\DBFilesClient\WorldMapArea.dbc"),
                  ('stock', r"D:\acore-classless\build\design\zones-extract\stock\patch-enUS-3\DBFilesClient\WorldMapArea.dbc")):
    d = zdbc.DBC(path)
    print(d.hdr())
    rows = {}
    for r in d.rows():
        # 3.3.5 layout: ID, MapID, AreaID, AreaName, LocLeft, LocRight, LocTop, LocBottom, DisplayMapID, DefaultDungeonFloor, ParentWorldMapID
        rows[r[0]] = dict(id=r[0], map=r[1], area=r[2], name=d.s(r[3]), L=f(r[4]), R=f(r[5]), T=f(r[6]), B=f(r[7]),
                          disp=r[8] if len(r) > 8 else None, parent=r[10] if len(r) > 10 else None)
    res[tag] = rows
    print(tag, 'rows', len(rows), 'id range', min(rows), max(rows))
    for k in (4, 13, 14, 37, 2061, 2062):
        print('   ', k, rows.get(k))

zf = zipfile.ZipFile(r"D:\ascension data till 10-9 11 am\Content.zip")
js = json.loads(zf.read('Content/WorldMapAreaData.json'))
res['content'] = {r['ID']: r for r in js}
print('content json rows', len(js), 'id range', min(r['ID'] for r in js), max(r['ID'] for r in js))
# offset test: content ID vs dbc ID matched by AreaName+bounds
cap = res['captured']
for off in (0, 1):
    ok = bad = miss = 0
    for r in js:
        c = cap.get(r['ID'] - off)
        if not c:
            miss += 1; continue
        if c['name'] == r['AreaName'] and abs(c['L'] - r['LocLeft']) < 1 and abs(c['T'] - r['LocTop']) < 1:
            ok += 1
        else:
            bad += 1
    print('offset', off, 'match', ok, 'mismatch', bad, 'missing', miss)
pickle.dump(res, open(OUT, 'wb'))
