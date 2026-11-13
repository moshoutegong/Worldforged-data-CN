# Privacy gate record

[简体中文](PRIVACY-GATE.md) · **English**

Run 2026-09-11 before the first commit, over all 35 text files (csv, json, md, py).

## Name gate (`leak_check2`: 2,723 person-name values from the LootCollector SavedVariables, plus the account and
character folder names of both Discord dumps; lc-key class vocabulary-filtered)

- Hits: 15 lines, all class `[lc-key]` (a capitalised LootCollector key that also matches a game word). **0 hits in
  the `[acct]` or `[char]` classes.**
- The 15 reduce to two tokens, both cleared:
  1. The Worldforged item name **"Signet of …'kes"** (item 354251 and its 7 ladder ids), 13 hits across 7 files.
     Verified against S1's itemcache: all 8 ids are present as class-4 (armor) items with item levels 48, 60, 64,
     70, 73, 77, 81, 88 — a Worldforged upgrade ladder. A game item, not a person.
  2. The word **"atlas"** inside the bisbeard source string `coa.bisbeard.com/atlas/atlas.json`, 2 hits. A URL path
     component, not a person.
- Nothing was redacted; nothing needed to be.

## Secret / e-mail / foreign-user-path scan

- 0 files flagged: no e-mail addresses, no Windows user paths other than the machine's own, no private-key or
  credential shapes.

## Standing rule

Never add raw LootCollector SavedVariables to this repository: they name finders, originators and voters. The
decoders under `tools/` read only the numeric fields `dt, i, z, x, y`.
