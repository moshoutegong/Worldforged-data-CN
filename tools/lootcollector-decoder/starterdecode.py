"""Decode our installed client's LootCollector_StarterDB (!LC1! + LibDeflate DecodeForPrint + raw deflate +
AceSerializer) and compare its Worldforged pins with the dump's LootCollector pins. Prints game data
(item ids, zone ids, counts) only; finder/originator/voter string values are never printed."""
import csv, re, zlib, collections, math

SRC = r"D:\games\ascension-live\Interface\AddOns\LootCollector_StarterDB\db.lua"
BD = r"D:\acore-classless\build\design"
ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()"
SIX = {c: i for i, c in enumerate(ALPHA)}


def decode_for_print(s):
    s = s.strip()
    out = bytearray()
    i = 0
    n = len(s)
    while i + 4 <= n:
        x1, x2, x3, x4 = (SIX[c] for c in s[i:i + 4])
        cache = x1 + x2 * 64 + x3 * 4096 + x4 * 262144
        out += bytes((cache & 255, (cache >> 8) & 255, cache >> 16))
        i += 4
    cache = bitlen = 0
    while i < n:
        cache += SIX[s[i]] << bitlen
        bitlen += 6
        i += 1
    while bitlen >= 8:
        out.append(cache & 255)
        cache >>= 8
        bitlen -= 8
    return bytes(out)


def unescape(t):
    def rep(m):
        c = m.group(1)
        return {"z": "\x1e", "{": "\x7f", "|": "~", "}": "^"}.get(c, chr(ord(c) - 64))
    return re.sub(r"~(.)", rep, t, flags=re.S)


def ace_deserialize(s):
    assert s.startswith("^1"), s[:10]
    toks = re.findall(r"\^(.)([^^]*)", s[2:], flags=re.S)
    pos = 0

    def val():
        nonlocal pos
        ctl, data = toks[pos]
        pos += 1
        if ctl == "S":
            return unescape(data)
        if ctl == "N":
            return float(data) if any(c in data for c in ".eE") else int(data)
        if ctl == "F":
            ctl2, e = toks[pos]
            pos += 1
            assert ctl2 == "f"
            return float(data) * 2.0 ** int(e)
        if ctl == "B":
            return True
        if ctl == "b":
            return False
        if ctl == "Z":
            return None
        if ctl == "T":
            t = {}
            while toks[pos][0] != "t":
                k = val()
                t[k] = val()
            pos += 1
            return t
        if ctl == "^":
            return None
        raise ValueError("ctl " + ctl)
    return val()


txt = open(SRC, encoding="utf-8").read()
body = re.search(r'data\s*=\s*"!LC1!([^"]+)"', txt).group(1)
raw = decode_for_print(body)
unz = zlib.decompress(raw, -15)
tbl = ace_deserialize(unz.decode("latin-1"))
print("StarterDB decoded: base64 chars", len(body), "| deflate bytes", len(raw), "| serialized bytes", len(unz))
print("top-level keys:", sorted(map(str, tbl.keys())))
disc = tbl.get("discoveries", {})
recs = list(disc.values()) if isinstance(disc, dict) else list(disc)
print("discoveries", len(recs))
keyc = collections.Counter(k for r in recs if isinstance(r, dict) for k in r)
print("record field names (counts):", dict(keyc.most_common(40)))
# shapes of the coords/zone fields only
ex = recs[0] if recs else {}
print("example (game fields only):", {k: ex.get(k) for k in ("itemID", "zoneID", "continent", "instanceZone", "coords", "discoveryType", "mergeCount", "status", "timestamp", "lastSeen") if k in ex})

wf_items = {int(r["item_id"]) for r in csv.DictReader(open(BD + r"\dump-lootcollector-wf-items.csv", encoding="utf-8"))}
pins = list(csv.DictReader(open(BD + r"\dump-lootcollector-wf-locations.csv", encoding="utf-8")))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


S = []
for r in recs:
    if not isinstance(r, dict):
        continue
    it, z = num(r.get("itemID")), num(r.get("zoneID"))
    c = r.get("coords") if isinstance(r.get("coords"), dict) else {}
    x, y = num(c.get("x")), num(c.get("y"))
    S.append((int(it) if it else None, int(z) if z else None, x, y, r.get("discoveryType", r.get("dt"))))
print("StarterDB dt values:", collections.Counter(s[4] for s in S).most_common(6))
s_items = {s[0] for s in S}
print("StarterDB distinct items", len(s_items), "| of the dump's 1,755 WF items present in StarterDB", len(wf_items & s_items),
      "| StarterDB items not in the dump's WF set", len(s_items - wf_items))
idx = collections.defaultdict(list)
for it, z, x, y, dt in S:
    idx[(it, z)].append((x, y))
exact = near = samezone = sameitem = 0
nearyd = []
for p in pins:
    it, z = int(p["item_id"]), int(p["lc_z_mapAreaId"])
    x, y = float(p["norm_x"]), float(p["norm_y"])
    cand = idx.get((it, z), [])
    if cand:
        samezone += 1
        d = min(math.hypot(x - a, y - b) for a, b in cand if a is not None and b is not None) if any(a is not None for a, b in cand) else 9
        if d < 0.00015:
            exact += 1
        if d <= 0.005:
            near += 1
    if it in s_items:
        sameitem += 1
print(f"dump WF unique pins {len(pins)}: same item+zone in StarterDB {samezone}, within 0.005 map units {near}, "
      f"identical to 4 dp {exact}, item present in StarterDB at all {sameitem}, item+zone ABSENT from StarterDB {len(pins) - samezone}")
