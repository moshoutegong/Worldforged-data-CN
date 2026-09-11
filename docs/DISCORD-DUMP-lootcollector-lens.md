# Dump lens: LootCollector SavedVariables = Worldforged item locations

Source: `D:\ascension data till 10-9 11 am\` — `Account.zip`, `Account (1).zip`, `Account (2).zip`.
Every archive was read **in memory** (Python `zipfile`); nothing was extracted and the dump was not modified.
Scripts: `build/design/dump-lootcollector-scripts/` (they print aggregates only).
Sidecars: `dump-lootcollector-wf-locations.csv` (4,284 unique WF pins with server X/Y) and
`dump-lootcollector-wf-items.csv` (1,755 WF items). Both carry game data only: item, zone, coordinates, GO entry.

> **Privacy.** LootCollector records **who** found each item. This report gives only the **existence and
> counts** of those fields (§9). Account folders are `<acct>` and character keys are `<char>`. Before
> commit, every output file was scanned against the 2,723 distinct person-name values in the SVs (§9).

---

## 0. Bottom line

| | measured |
|---|---|
| LootCollector SV files | **6**: one `LootCollector.lua` and one `.lua.bak` in each of the 3 account zips |
| raw discovery records | **18,123** (plus 129 black-market-vendor records) |
| after dedupe on (realm, GUID) | **10,391**; **4,700** distinct GUIDs across realms |
| distinct item ids | **2,065** |
| distinct (item, zone, x, y) locations | **4,699** (4,678 distinct spots if the item is ignored) |
| **Worldforged** (`dt = 1`) | **9,264** deduped records → **1,755 items**, **4,284 unique pins** (cross-realm) |
| Mystic Scroll (`dt = 2`) | 1,119 records, 309 items |
| WF items in our 55,454 cached item ids | **1,745 / 1,755** (all Ascension-only; **0** in the live `item_template`) |
| WF items in the dump's harvest itemcache TSV | **1,740 / 1,755** (names, ilvl, reqLevel) |
| WF item level | min 0 / median **42** / max **73**; reqLevel 1 / 36 / 60 |
| server maps of the WF pins | map 0: **2,389**, map 1: **1,775**, map 530: 54, instances: 66 over 19 maps; **Northrend 0, Pale Reach 0** |
| map → server conversion | exact inverse of the client projection; checked on **32,485** dump spawns (median error 1.4–1.7 yd, which is entirely their own 1-dp input rounding) |
| accuracy of a pin vs. the real spawn | median **3.5 yd** against maintainer-verified coordinates (60 records); tail 10–54 yd; **2 of 11** verified items have pins **670–750 yd** off |
| a dump gameobject within 5 yd of the pin | **1,548 / 4,108** pins (37.7%); within 10 yd **2,328** (56.7%) |
| height (Z) | **ABSENT**: LootCollector stores no Z |

**Delta over what we held.** Before this dump we had **zero** Worldforged spawn locations. We now have 4,284
WF pins with server X/Y for 1,755 items. 37.7% of them sit within 5 yd of a dump gameobject, which gives
999 candidate spawn-object entries (571 of them Ascension-only GO templates already in our WDB cache).

---

## 1. Files

| zip | file | bytes | discovery records | realms present (records) |
|---|---|---:|---:|---|
| Account.zip | `<acct>/SavedVariables/LootCollector.lua` | 8,034,390 | 5,680 | Area 52 - Free-Pick 2,047 · Dawnrise - Season 10 Freepick 2,078 · Vol'jin - Conquest of Azeroth 1,552 · Bronzebeard - Warcraft Reborn 3 |
| Account.zip | `….lua.bak` | 2,569,062 | 2,464 | Vol'jin 2,464 |
| Account (1).zip | `<acct>/SavedVariables/LootCollector.lua` | 7,922,228 | 5,141 | Darkmoon - Season 10 Wildcard 2,005 · Area 52 1,592 · Vol'jin 1,544 |
| Account (1).zip | `….lua.bak` | 2,235,264 | 1,674 | Vol'jin 1,674 |
| Account (2).zip | `<acct>/SavedVariables/LootCollector.lua` | 3,286,414 | 1,545 | Vol'jin 1,545 |
| Account (2).zip | `….lua.bak` | 1,885,227 | 1,619 | Vol'jin 1,619 |

Each zip has exactly one account folder containing LootCollector. `wtf.zip` has none. `.rar` files were not read (no extractor on this machine).
Top-level variable: `LootCollectorDB_Asc` (AceDB layout: `char`, `profileKeys`, `profiles`, `global`, `schemaVersion`).
Parser: a purpose-written Lua-table tokenizer and recursive-descent parser (`luasv.py`). All 6 files parsed with 0 errors.

**Semantics source.** The field meanings below are confirmed against the addon's own source in **our** installed
client: `D:\games\ascension-live\Interface\AddOns\LootCollector` v1.0.6 (`Modules/Core.lua`, `Detect.lua`,
`Constants.lua`, `CoordAuthority.lua`). That source is **not from the dump**; I used it only as documentation.
13 records carry `av = 1.0.4r-beta`, so the dump was written by an older build of the same addon.

## 2. Schema

```
LootCollectorDB_Asc
 ├─ char["<char> - <realm>"]        48 entries over 6 files: looted{GUID→ts} (890), mapFilters, migration flags
 ├─ profileKeys                     48 entries (character keys; counted only)
 ├─ profiles                        UI settings
 └─ global
     ├─ realms["<realm>"]
     │    ├─ discoveries[GUID] = { discovery record, see below }
     │    └─ blackmarketVendors[key] = { c,z,iz,xy,i,il,q,s,st,t0,ls,dt,fp,o,g,mid,
     │                                   vendorName, vendorType, vendorItems[n]{itemID,link,name,price,stack,costs,…} }
     ├─ scannerData[itemLink] = { isWF, isCollected, reqLevel }   per-item tooltip-scan cache, 2,320 item ids
     ├─ newWorldforgedItems[itemId] = true                         306 ids
     ├─ deletedCache[mid] = { payload{c,z,iz,i,il,mid,xy,t0}, deletedAt, expiresAt, … }
     ├─ aoeTombstones[n] = { c,z,iz,x,y,radius,expires,name,dt }  42 rows
     └─ cacheQueue, migration flags
```

### Discovery record fields (from 18,123 raw records)

| key | type | meaning | evidence |
|---|---|---|---|
| `g` | str | GUID `c-z-iz-i-x-y` (identical to the table key) | 18,123/18,123 equal |
| `c` | int | addon's **logical continent**: 1 Kalimdor, 2 Eastern Kingdoms, 3 Outland, 0 unknown | code; values 0/1/2/3 = 9/8,228/9,883/3 raw |
| `z` | int | `GetCurrentMapAreaID()` = **WorldMapArea.dbc ID + 1** | code; §4 |
| `iz` | int | instance zone: 0 when the zone is in the addon's ZoneList, otherwise = mapAreaID | code; ≠0 in 8 deduped records (all z=2022, Atal'Hakkar) |
| `i` | int | item id | 18,123/18,123 equal to the GUID's 4th part |
| `il` | str | item link (`|cff…|Hitem:…|h[Name]|h|r`), which names the item | 100% present |
| `xy.x`, `xy.y` | float | `GetPlayerMapPosition("player")` at loot time, rounded to 4 dp, normalised 0..1 within WMA(z−1) | code; all values ≤4 dp; x 0.0192–0.9614, y 0.0131–0.9997 |
| `dt` | int | discovery type: 1 WORLDFORGED, 2 MYSTIC_SCROLL, 3 BLACKMARKET (vendors table); **4 is not in the addon's enum** | `Constants.DISCOVERY_TYPE` |
| `q` | int | item quality | 0–7 |
| `it`, `ist` | int | addon's item type / subtype ids | code |
| `cl` | str | **item's** class-restriction abbreviation (`wa`,`ma`,`lo`=warlock,…; `cl` = no class token) — **not** the finder's class | `GetItemClassAbbr` |
| `s` | str | status: CONFIRMED / UNCONFIRMED / FADING / STALE (decay) | 4 values |
| `t0`, `ls`, `st` | int | first seen / last seen / status-change unix time | t0 2025-10-03 → 2026-08-20, ls ≤ 2026-09-04 |
| `mc` | int | merge/confirmation count, capped at 1000 | code; 1–1370 observed |
| `ac`, `at`, `nd`, `adc`, `pendingAnnounce` | int | announce/sync bookkeeping | not needed |
| `src` | int/str | loot source: `world_loot`=0 / `npc_gossip`=1 / `emote_event`=2 / `direct`=3 (MS only) | `Constants.AcceptedLootSrc*` |
| `mid` | str | 8-hex message id; **1:1 with `g`** (4,700 ↔ 4,700, no collisions either way) | measured. The code says FNV-1a-32 over `BuildDiscoveryMidPayload`; my reconstruction with the default payload matched 0/10,391, so **the hash input was NOT reproduced** |
| `fp`, `o`, `fp_votes{name→{score,t0}}`, `ack_votes`, `s_flag` | | finder / originator / voter **names** | **§9: counted only** |
| `_ln`, `_lz`, `_rawC`, `_rawZ`, `_rawIz`, `_rawIl` | | legacy-import fields (1,597–1,611 records). `_lz` holds "stranglethorn vale" for 77 different z, so it is **unreliable** | measured |

## 3. The composite key `<a>-<b>-<c>-<itemId>-<x>-<y>`

`GUID = c - z - iz - itemId - x - y` (`L:GenerateGUID(c, z, iz, i, x, y)`, x/y formatted `%.4f`).

- **a = `c` = the addon's logical continent**. It is **not faction** and **not the server map**. Measured: the
  addon puts the map-530 zones on the continent their players reach them from (Azuremyst/Bloodmyst → `c=1`,
  Eversong/Ghostlands → `c=2`), and dungeons carry the continent of their entrance.
  **Take the server map from `WMA(z−1).MapID`, never from `c`.**
- **b = `z` = mapAreaID** (WorldMapArea ID + 1).
- **c = `iz` = instance zone** (0 in the open world).
- There is **no faction and no realm in the key**. Realm is the parent table. Faction is **ABSENT** from records.
- Key x/y vs the stored `xy`: identical for **9,310 / 10,391** deduped records. Otherwise median 0.00, p90 0.34,
  p99 99.7, max 372.8 yd. The addon's deduplicator and CoordAuthority move the stored `xy` while the GUID keeps the
  first-seen point. **Use `xy`, not the key.**

## 4. Counts and dedupe

| step | count |
|---|---:|
| raw discovery records (6 files) | 18,123 |
| distinct (realm, GUID) | **10,391** |
| … from `.lua` only | 7,706 (`.bak` adds **2,685** that were later pruned from the live file) |
| (realm, GUID) seen in 1 / 2 / 3 accounts | 6,821 / 2,005 / 1,565 |
| distinct GUID across realms | **4,700** — on 1 realm 2,655 · 2 realms 40 · 3 realms 364 · 4 realms 1,641 |
| deduped per realm | Vol'jin 4,250 · Dawnrise 2,078 · Area 52 2,055 · Darkmoon 2,005 · Bronzebeard 3 |
| distinct items | 2,065 |
| distinct (item, z, x4, y4) | 4,699 |
| distinct (item, z, x2, y2) (~1% grid) | 3,322 |
| deduped status | FADING 4,862 · CONFIRMED 4,754 · STALE 732 · UNCONFIRMED 43 |
| deduped `dt` | 1 (WF) 9,264 · 2 (MS) 1,119 · 4 (undocumented) 8 = 2 items: *Frightened Kitten*, *Prophecy of the Arcanist* |

**These are not independent observations.** 1,641 GUIDs appear identically on 4 realms, and `fp_votes` holds
29,390 voter entries from 2,064 distinct voters. The data is **crowd-synced** across the addon's channel and
starter DB. It is not what three players looted themselves.

## 5. Worldforged

Definition: `dt = 1` (`DISCOVERY_TYPE.WORLDFORGED`; the addon sets it from a tooltip "Worldforged" scan plus a curated id list).

| check | result |
|---|---:|
| WF items (dt=1) | **1,755** |
| … `scannerData.isWF = true` | 1,736 (19 scanned `false`: they qualified via the curated list) |
| … in `global.newWorldforgedItems` | 106 of its 306 ids |
| scanner `isWF=true` items **without** a pin | 164 |
| installed addon's `WorldforgedList.lua` (our client, not the dump) | 1,834 ids; 1,636 overlap the dump's 1,755; **198 listed WF ids have no pin** |
| unique WF pins (item, z, x4, y4), merged across realms | **4,284** |

**Item level** (harvest itemcache TSV `itemcache-dawnrise-2026-09-01c.tsv`, 548,496 rows; 1,740 of 1,755 WF items matched):

| ilvl | 0–9 | 10–19 | 20–29 | 30–39 | 40–49 | 50–59 | 60–69 | 70–79 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| items | 82 | 305 | 232 | 169 | 310 | 373 | 267 | 2 |

Quality (TSV): common 5 · uncommon 758 · rare 920 · epic 54 · quality 6: 3. The invTypes cover every armour/weapon
slot (most common: 17 two-hand 231, 13 one-hand 172, 12 trinket 118, 26 ranged 112, 11 finger 99).
Id bands (`id // 100000`): 3xxxxx 237 · 4xxxxx 682 · 5xxxxx 687 · 13xxxxx 87 (Worldforged Scrolls) · others ≤ 24.
WF items missing from the TSV (15): 100369, 131059, 132418, 132426, 132599, 132626, 132636, 132637, 132690,
132693, 132698, 132704, 132723, 134869, 201537. Their names still come from `il`.
**The full id / name / ilvl / reqLevel / pin list is in `dump-lootcollector-wf-items.csv`.**

### Item-id joins

| set | n | in our 55,454 cached ids | Ascension-only (cached − live) | in live `item_template` | in harvest TSV | in none |
|---|---:|---:|---:|---:|---:|---:|
| all LootCollector items | 2,065 | 1,746 | 1,746 | **0** | 1,743 | 309 (307 are Mystic Scrolls) |
| Worldforged | 1,755 | 1,745 | 1,745 | **0** | 1,740 | 2 |

Every WF item has to be **created** in `item_template` (none exist live). 1,745 of them already have an enumerated id in our cache.

## 6. Zone distribution

`z − 1` resolves to a row of the captured `WorldMapArea.dbc` for **111 / 111** WF zone values (0 unmapped).
That DBC (md5 `385136e3…`, 310 rows) is **byte-identical** to the one extracted from Ascension's `patch-M.MPQ`.
47 of the zones are stock WMA rows; **64 are Ascension-custom** (starting areas, caves, mines, secret dungeons, WMA 1200–1245 / 2021–2030).

Unique WF pins by server map: **0 → 2,389 · 1 → 1,775 · 530 → 54** (Eversong, Ghostlands, Azuremyst,
Bloodmyst, Exodar, Silvermoon, Sunstrider/Ammen starts) · instances 66 pins over 19 maps (Maraudon 19,
Deadmines 12, Magisters' Terrace 10, Atal'Hakkar 5, …). **Northrend (571): 0. Pale Reach (WMA 2062 / z 2063): 0 — ABSENT.**

Top 30 zones by unique WF pins (`go≤5` = pins with a dump gameobject within 5 yd):

| z | WMA | name | map | WMA source | pins | items | go≤5 |
|---:|---:|---|---:|---|---:|---:|---:|
| 38 | 37 | Stranglethorn | 0 | stock | 195 | 103 | 63 |
| 40 | 39 | Westfall | 0 | stock | 130 | 67 | 44 |
| 27 | 26 | Hinterlands | 0 | stock | 128 | 82 | 35 |
| 12 | 11 | Barrens | 1 | stock | 128 | 75 | 25 |
| 17 | 16 | Arathi | 0 | stock | 126 | 68 | 59 |
| 16 | 15 | Alterac | 0 | stock | 122 | 73 | 56 |
| 41 | 40 | Wetlands | 0 | stock | 116 | 79 | 24 |
| 142 | 141 | Dustwallow | 1 | stock | 114 | 59 | 39 |
| 102 | 101 | Desolace | 1 | stock | 114 | 58 | 46 |
| 122 | 121 | Feralas | 1 | stock | 114 | 66 | 27 |
| 24 | 23 | EasternPlaguelands | 0 | stock | 112 | 82 | 35 |
| 162 | 161 | Tanaris | 1 | stock | 111 | 64 | 23 |
| 202 | 201 | UngoroCrater | 1 | stock | 111 | 60 | 63 |
| 35 | 34 | Duskwood | 0 | stock | 109 | 65 | 35 |
| 31 | 30 | Elwynn | 0 | stock | 105 | 52 | 36 |
| 5 | 4 | Durotar | 1 | stock | 103 | 52 | 46 |
| 44 | 43 | Ashenvale | 1 | stock | 101 | 53 | 25 |
| 62 | 61 | ThousandNeedles | 1 | stock | 101 | 41 | 39 |
| 21 | 20 | Tirisfal | 0 | stock | 95 | 47 | 38 |
| 18 | 17 | Badlands | 0 | stock | 95 | 59 | 47 |
| 43 | 42 | Darkshore | 1 | stock | 93 | 54 | 15 |
| 30 | 29 | BurningSteppes | 0 | stock | 93 | 67 | 39 |
| 39 | 38 | SwampOfSorrows | 0 | stock | 92 | 61 | 47 |
| 29 | 28 | SearingGorge | 0 | stock | 86 | 54 | 47 |
| 36 | 35 | LochModan | 0 | stock | 83 | 38 | 32 |
| 42 | 41 | Teldrassil | 1 | stock | 83 | 52 | 18 |
| 23 | 22 | WesternPlaguelands | 0 | stock | 81 | 44 | 34 |
| 28 | 27 | DunMorogh | 0 | stock | 77 | 44 | 21 |
| 37 | 36 | Redridge | 0 | stock | 75 | 36 | 40 |
| 182 | 181 | Aszhara | 1 | stock | 72 | 46 | 36 |

Ascension-custom zones carry 524 pins; the largest (deduped records, realm-counted) are *campnarachestart* 80,
*northshire* 74, *deathknellstart* 71, *shadowglenstart* 70, *valleyoftrialsstart* 65, *coldridgevalley* 56.

## 7. Normalised x/y → server X/Y

```
row      = WorldMapArea[z - 1]              # captured DBC == Ascension patch-M; NOT the stock 3.3.5 DBC
map      = row.MapID
server_X = row.LocTop  - y * (row.LocTop  - row.LocBottom)     # top/bottom are X
server_Y = row.LocLeft - x * (row.LocLeft - row.LocRight)      # left/right are Y
server_Z = ABSENT (not recorded) -> take nearest GO z (CSV column) or query terrain/vmap height
```

Use `xy` (not the GUID's x/y) and average `xy` over the copies of a pin (that is what the locations CSV does).

### How accurate, measured separately

| source of error | measured |
|---|---|
| **formula** (the exact inverse of the client projection), tested on the dump's own spawn records that carry both MapX/MapY and internal X/Y: 21,931 GO + 3,436 NPC + 7,118 Bronzebeard GO = **32,485** | median error 1.43 / 1.65 / 1.56 yd; p99 4.3–5.1 yd. The RMS **expected** from those records' 1-decimal MapX/MapY rounding is 1.49 / 1.83 / 1.57 yd, so the formula contributes **~0 error**. (Skipped: 767 records with MapX/MapY outside 0–100, 92 on a map mismatch, 964 with unmatched map names.) |
| LootCollector's 4-dp quantisation | half-step median **0.20 yd**, max 1.84 yd (largest zones) |
| using the stock 3.3.5 WMA bounds instead of Ascension's (Ascension rounded the bounds to whole yards) | shift median 0.61, p99 1.02, max 1.19 yd. **Use the captured/patch-M bounds**, since the client projected with them |
| **what the point is**: `GetPlayerMapPosition` when the loot window opened = the **player**, not the object | against the 11 maintainer "stand-on-spawn" rows in the addon's `CoordAuthority.lua` (our client): 60 dump records for those items, **median 3.5 yd**. For 9 items the closest copy is 0.0–3.5 yd and the worst copy 9.8–53.7 yd. **2 items (410154, 515415) are 673–750 yd off in every copy**; these are the wrong pins the maintainer later overrode |
| same-map nearest **dump gameobject** to each WF pin (4,108 pins on maps with GO coverage) | median **7.8 yd** (p25 3.4, p75 19.8, p90 80.0); ≤3 yd 871 · ≤5 yd **1,538** · ≤10 yd 2,328 · ≤25 yd 3,241. Stock-WMA zones median 7.9, Ascension-custom zones median 7.6: the custom bounds convert as well as the stock ones |
| nearest dump NPC | median 76.6 yd (only 213 pins have any NPC coverage), consistent with WF items being object pick-ups, not creature drops |
| instance maps (66 pins) | WMA bounds applied, but multi-floor dungeons use per-floor DungeonMap bounds and LootCollector records no floor, so these are **UNVERIFIED** |

**Honest summary:** the conversion is exact. A pin is where a player stood when looting, typically within
~2–8 yd of the spawn, with a long tail and a small share of plainly wrong pins. Status FADING/STALE and
`mc = 1` pins deserve less trust. Snapping each pin to the nearest dump gameobject within ≤5 yd is the
recommended refinement where one exists.

### What sits under the pins (candidate WF spawn objects)

Within 5 yd: **1,548 pins → 999 distinct GO entries**. 611 of those entries are in our WDB GO-template cache and
**571 are Ascension-only**. 979 of the 999 are nearest to exactly one WF item, 20 to more than one, which suggests
roughly one spawn object per item. The GO names are world-prop pick-ups (*Forgotten Sack*, *Stuck Sword*,
*Adventurer's Corpse*, *Disturbed Dirt*, *Abandoned Bag*, *Travel Sack*, *Stolen Supplies*, …).
**CLAIM, not verified:** the Bronzebeard CSV `Type` column labels 1,154 of them "Door" and 133 "Chest";
I did not validate that column's enum. **Nearest is not the same as source.** The GO→item binding is a lead, not a fact.

## 8. Black-market vendors (side table)

129 raw records (`vendorType`: BM 107 · MS 14 · EX 8), same `c/z/iz/xy` layout. `vendorItems`: 517 entries
covering 130 item ids. The vendor NPC name field exists (§9). These give vendor positions, not WF drops; not pursued further.

## 9. Privacy: fields that can hold person names (existence and counts only)

| field | occurrences | distinct values |
|---|---:|---:|
| `discoveries.fp` (finder) | 18,123 | 1,218 |
| `discoveries.o` (originator) | 18,123 | 1,123 |
| `discoveries.fp_votes` keys (voters) | 29,390 | 2,064 |
| `discoveries.ack_votes` keys | 4 | 3 |
| `discoveries._ln` (legacy; shape consistent with item names, not verified) | 1,611 | 1,491 |
| `blackmarketVendors.fp` / `.o` | 129 / 129 | 12 / 12 |
| `blackmarketVendors.vendorName` (NPC) | 129 | 21 |
| `aoeTombstones.name` | 42 | — |
| `char` keys (`<char> - <realm>`) / `profileKeys` | 48 / 48 | — |
| `char.looted` GUID markers (per character) | 890 | — |

No email, IP, password, token or session value exists in the LootCollector SVs. No account or character name
appears in this report or its sidecars. Output scan: both CSVs were tokenised and matched against the 2,723
person-name values. Every hit (51 in the locations CSV, 18 in the items CSV) was a word inside an `item_name`
that also appears in the itemcache / WMA **game vocabulary**, i.e. a player named after an in-game word, not a leaked name.

## 10. What is ABSENT

- **Z / height** for every pin.
- **Faction**. Also no source-object or creature id: which GO or NPC dropped the item is not recorded.
- Any pin in **Northrend** or **Pale Reach**.
- A machine-checkable proof that a pin's nearest GO is its spawn object.
- Independence: the records are crowd-synced (§4), so three accounts are not three samples.

## 11. Method (reproducible)

`luasv.py` (parser) → `skeleton.py` / `profile.py` / `fields.py` (sanitised schema; string values reduced to
letter/digit shapes) → `keys.py` / `prec.py` (GUID decomposition) → `wma.py` (DBC + `Content/WorldMapAreaData.json`:
the JSON's `ID` = DBC ID + 1 for 131 of 172 rows, 0 matches at offset 0, which confirms `z = WMA ID + 1`) →
`itemjoin.py` (TSV join) → `spawns.py` (dump spawns + formula validation) → `main.py` (dedupe, WF, zones,
conversion, nearest GO) → `authority.py` → `goids.py` → `sidecar.py` → `privcheck.py` / `privcol.py`.
