# Worldforged data

[简体中文](README.md) · **English**

Everything SUNDERBORN holds about Project Ascension's **Worldforged** system, consolidated from six sources into one
place, with provenance and privacy notes. Assembled 2026-09-11 from the SUNDERBORN audits (`D:\acore-classless`).
Local repository; nothing is published.

## The system in one paragraph

Worldforged items are Ascension-custom items picked up from **world props** (sacks, stuck weapons, corpses, disturbed
dirt), not from the 25 "Worldforged Cache" objects: 0 of the 4,284 dump pins lie within 5 yd of a cache. Every base
item has a **7-tier upgrade ladder** (Base, Lvl 60, ZG, MC, BWL, AQ40, Naxx), each tier its own item id, with S1 item
levels rising by a median of +4 (Lvl 60) up to +28 (Naxx). Items roll **random suffixes per roll** (the suffix name
does not determine the stats). `ItemVariationData.json` (Normal / Heroic / Bloodforged / Mythic) does **not** cover
Worldforged: 0 of the 1,755 WF items is a Normal base, and 725 WF ids sit inside Mythic arrays as id collisions.

## Files

| File | Rows | What it is |
|---|---|---|
| `data/wf_pins_union.csv` | **5,703 pins / 1,973 items** | **The master pickup-location table.** StarterDB 1,970 pins + Discord zips +1,125 + Discord RARs +2,608. Per pin: item, S1 ilvl/req level, LootCollector zone id, WorldMapArea id and name, server map, map-percent x/y, server X/Y, which sources hold it, record count. |
| `data/wf_items_union.csv` | 1,973 | One row per item: pin counts by source, server maps, zones. |
| `data/exiles_wf_ladder.csv` | 13,953 | **The upgrade ladder by name**, from the db.exil.es mirror: 1,849 names x tier -> item id, S1 item level and required level, "Found at" zone + map coords, whether the name has all 7 tiers (1,787 do). |
| `data/lootsmith/wf_upgrade_chains.json` | 1,978 chains | **The upgrade ladder by id**, from LootCollector's `Modules/WorldforgedUpgrades.lua` (harvested 2026-08-27 by Lootsmith): base id -> { tier: item id }, 6 tier names. Cross-check against the name ladder. |
| `data/lootsmith/lootcollector_wf.json` | | LootCollector's own Worldforged flag and required level per item: an independent check of "is this item Worldforged". |
| `data/lootsmith/bisbeard_atlas_wf_locations.json` | 1,481 items / 49 zones | A **third location source**: the bisbeard community atlas (coa.bisbeard.com/atlas), harvested 2026-08-28. `loc[name] = [[zoneIndex, x, y], ...]`, `zones[]` by index. |
| `data/lootsmith/bisbeard_atlas_data.json` | | The same atlas grouped by kind. |
| `data/provenance/dump_zips_wf_*.csv` | 1,755 items / 4,284 pins | The original zip-only extraction, exactly as published in `DISCORD-DUMP-VERDICT.md` section 2 (pins at exact 4 dp, so the count differs from the 0.005-deduped union). |
| `data/worldmaparea_bounds_captured.csv` / `_stock.csv` | 310 / 108 | The WorldMapArea bounds used for the conversion: Ascension's captured table and stock 3.3.5. |
| `tools/build_pin_union.py`, `tools/build_exiles_ladder.py` | | The generators. Re-runnable; read-only on every input. |
| `tools/lootcollector-decoder/` | | The privacy-preserving LootCollector SavedVariables decoder (`!LC1!` + LibDeflate print encoding + raw deflate + AceSerializer) and helpers. |
| `docs/DISCORD-DUMP-lootcollector-lens.md` | | The full measurement report behind the zip extraction. |

## Coordinates: what a pin is, and how it was converted

- A LootCollector pin is the **looter's position at pickup time**, not the spawn point. Median 3.5 yd from the
  maintainer-verified spawn; 2 of 11 verified items were 670-750 yd off. **Z is absent everywhere.**
- Map-percent coords -> server X/Y: `X = Top - y*(Top - Bottom)`, `Y = Left - x*(Left - Right)`, with the LootCollector
  zone `z = WorldMapArea id + 1`, using Ascension's **captured** WMA bounds (`worldmaparea_bounds_captured.csv`), not
  stock. Verified on 32,485 dump spawns: median error 1.4-1.7 yd, which is the source's own 1-dp rounding.
- Dedupe rule for the union: one pin per (item, zone) within 0.005 map units. This is the rule the Discord verdict used.
- 1,548 of the 4,108 zip pins on maps with object coverage had a dump gameobject within 5 yd: the pickup props exist,
  but which prop type each item comes from is not recorded.

## Coverage

| Server map | Pins |
|---|---|
| 0 Eastern Kingdoms | 2,939 |
| 1 Kalimdor | 2,243 |
| 530 Outland | 65 |
| instances (19 maps; e.g. 189, 329, 36, 429, 47) | ~450 |
| **Northrend** | **0** |
| **Pale Reach** | **0** |

## Sources and how far to trust each

| Source | Gives | Trust |
|---|---|---|
| Installed client `LootCollector_StarterDB` v7.0 (folder 2026-08-20) | 1,970 pins / 1,600 items | Public addon data shipped with the client; the base layer. |
| Discord dump LootCollector SavedVariables (3 zips + 6 RARs) | +1,125 / +2,608 pins, +155 / +218 items | Real player captures. **Records carry finder names**; only numeric fields were read. |
| db.exil.es mirror (baseline 2026-08-29) | the 7-tier ladder by name, S1 ilvls, "Found at" | Best-effort scrape: 1,230 of 1,849 names have more than one Base-tier id; 9 ladders repeat an id within a tier; the site's displayed ilvl differs from S1 on 2,289 of 13,953 WF pages (**use S1's**). |
| LootCollector `WorldforgedUpgrades.lua` (via Lootsmith) | 1,978 id-level chains | Addon data; the id-level truth for upgrades. Cross-check with the name ladder before use. |
| bisbeard community atlas (via Lootsmith) | 1,481 items / 49 zones of pins | Community-sourced, supporting evidence only. |
| S1 (`hertigservices/ascension-data`) itemcache | item bodies and ilvl for all 13,953 WF ids | The item-data authority. |
| `ItemVariationData.json` (client `Data/Content`, 3.8 MB) | **not a WF source** | 0 WF bases; 725 WF ids and 1,244 of our own ids collide inside its Mythic arrays. Never import its Mythic arrays as-is. |
| Repack world DB | nothing | 0 custom loot or vendor rows. |
| 25 Worldforged Cache positions (dump gameobject positions; map 0: 10, map 1: 15) | object positions only | 10 have chest templates, 15 none; **loot tables absent**; they are not the pickup sites. See `DISCORD-DUMP-VERDICT.md` section 2.1. |

## Gaps (what no source holds)

- **Z** for every pin (terrain lookup gives a usable Z for about 63 % of points; off by more than 10 yd for about 21 %).
- **Spawn points and prop types** (pins are looter positions; the sack/weapon/corpse type is not recorded).
- **Random-suffix magnitudes** exist only in game: the bisbeard feed's 13,951 affixed items lack the suffix line entirely
  (Lootsmith finding, 2026-08-22).
- **Drop and pickup rates**: nothing measured anywhere (the Exiles "Observed" column is 0 on every row).
- **The upgrade mechanic / NPC** server side: the ladder is data only; how Ascension consumed it is not held.
- **Northrend and Pale Reach**: 0 pins in every source.

## Privacy

LootCollector records name the finder, originator and voters. **This repository contains none of that.** The decoders
read only the numeric fields `dt, i, z, x, y`; every file was scanned with the project's name gate (`leak_check2`,
2,723 known person-name values plus the account/character folder names) before commit. Never add raw SavedVariables here.

## How the numbers were checked

- The pin union reproduces `DISCORD-DUMP-VERDICT.md` section 9 exactly: 1,970 + 1,125 + 2,608 = **5,703 pins**;
  1,600 + 155 + 218 = **1,973 items**; all 1,973 named from S1.
- The ladder reproduces `exiles-loot-quests.md` section 8: 13,953 ids, 1,849 names, 1,787 complete ladders,
  S1 ilvl for 13,953 of 13,953; median gains Lvl 60 +4, ZG +10, MC +13, BWL +17, AQ40 +21, Naxx +28.

## Relation to the SUNDERBORN plan

- **AD5 / DA5, Worldforged upgrades on realm 2:** build the lookup table now (this repository's two ladders, reconciled),
  the upgrade NPC later.
- Every new item id needs a client `Item.dbc` row (AD7) or it is invisible when equipped.
- Pickup spawns cannot be class-gated, so realm-2-only Worldforged needs phasing or a realm-2-only map.
- Tier unlocks can key off `mod-individual-progression` (MC / BWL / AQ40 / Naxx), which is already enabled.
