# 世界铸造数据

**简体中文** · [English](README.en.md)

本仓库整理了 SUNDERBORN 项目收集的 Project Ascension（飞升）**世界铸造（Worldforged）**数据，汇总六类来源，并附上数据出处和隐私说明。原始资料于 2026 年 9 月 11 日从 SUNDERBORN 的审计记录（`D:\acore-classless`）整理而来，当时保存在本地仓库。

上游项目：[Tareksoh/Worldforged-data](https://github.com/Tareksoh/Worldforged-data)。

## 世界铸造系统

飞升的世界铸造物品可从**场景物件**拾取，例如袋子、插在地上的武器、尸体和翻动过的泥土。原始导出的 4,284 个点位中，没有一个落在那 25 个「世界铸造宝箱」（Worldforged Cache）的 5 码范围内。每件基础物品有 **7 个升级档次**：基础、60 级、祖尔格拉布（ZG）、熔火之心（MC）、黑翼之巢（BWL）、安其拉神殿（AQ40）和纳克萨玛斯（Naxx）。各档次有独立的物品 ID。按 S1 数据计算，物品等级增幅的中位数从 60 级档的 +4 到纳克萨玛斯档的 +28。

每次生成物品时会随机掷出词缀，词缀名称无法确定具体属性。对照 `ItemVariationData.json`（普通、英雄、血铸、史诗）时，1,755 个世界铸造物品中没有任何一个属于普通档基础物品，有 725 个 ID 与史诗档数组中的 ID 冲突。

## 文件

| 文件 | 记录数 | 内容 |
|---|---|---|
| [wf_pins_union.csv](data/wf_pins_union.csv) | **5,703 个点位 / 1,973 个物品** | 拾取点位总表。StarterDB 收录 1,970 个点位，Discord ZIP 和 RAR 存档分别补入 1,125 和 2,608 个。每行包含物品、S1 物品等级和所需等级、LootCollector 区域 ID、WorldMapArea ID 和名称、服务器地图 ID、地图比例坐标、服务器 X/Y、收录来源与记录数。 |
| [wf_items_union.csv](data/wf_items_union.csv) | 1,973 | 每件物品一行，列出各来源的点位数、服务器地图和区域。 |
| [exiles_wf_ladder.csv](data/exiles_wf_ladder.csv) | 13,953 | 从 db.exil.es 镜像整理的**按名称归组的升级表**。按 1,849 个物品名称及升级档次列出物品 ID、S1 物品等级和所需等级、拾取区域及地图坐标。其中 1,787 个名称的 7 档齐全。 |
| [wf_upgrade_chains.json](data/lootsmith/wf_upgrade_chains.json) | 1,978 条升级链 | Lootsmith 于 2026 年 8 月 27 日从 LootCollector 的 `Modules/WorldforgedUpgrades.lua` 提取的**按 ID 归组的升级表**。每个基础 ID 对应 6 个升级档次的物品 ID，可与按名称整理的表互相核对。 |
| [lootcollector_wf.json](data/lootsmith/lootcollector_wf.json) | | LootCollector 自身的世界铸造标记和所需等级，可用于交叉核对物品归类。 |
| [bisbeard_atlas_wf_locations.json](data/lootsmith/bisbeard_atlas_wf_locations.json) | 1,481 个物品 / 49 个区域 | 来自 Bisbeard 社区地图（coa.bisbeard.com/atlas），于 2026 年 8 月 28 日采集。`loc[name] = [[zoneIndex, x, y], ...]` 中的区域索引对应 `zones[]`。 |
| [bisbeard_atlas_data.json](data/lootsmith/bisbeard_atlas_data.json) | | 同一份社区地图数据，按类型归组。 |
| `data/provenance/dump_zips_wf_*.csv` | 1,755 个物品 / 4,284 个点位 | 仅从 ZIP 存档提取的原始结果，对应 `DISCORD-DUMP-VERDICT.md` 第 2 节。坐标保留 4 位小数，因此数量与按 0.005 地图单位去重的总表不同。 |
| [worldmaparea_bounds_captured.csv](data/worldmaparea_bounds_captured.csv) / [worldmaparea_bounds_stock.csv](data/worldmaparea_bounds_stock.csv) | 310 / 108 | 坐标转换所用的 WorldMapArea 边界，分别来自飞升采集表与原版 3.3.5。 |
| [build_pin_union.py](tools/build_pin_union.py)、[build_exiles_ladder.py](tools/build_exiles_ladder.py) | | 数据生成脚本，可重复运行，输入文件以只读方式处理。 |
| [lootcollector-decoder](tools/lootcollector-decoder/) | | 注重隐私的 LootCollector SavedVariables 解码器及辅助工具，支持 `!LC1!`、LibDeflate 可打印编码、原始 DEFLATE 和 AceSerializer。 |
| [DISCORD-DUMP-lootcollector-lens.md](docs/DISCORD-DUMP-lootcollector-lens.md) | | ZIP 数据提取与测量的完整报告。 |

## 点位含义与坐标转换

- LootCollector 点位记录的是**玩家拾取时的位置**。与维护者核实的生成点比较，偏差中位数为 3.5 码。核实的 11 件物品中，有 2 件偏离 670–750 码。所有点位都缺少 **Z（高度）**。
- 地图比例坐标转为服务器 X/Y 的公式为 `X = Top - y*(Top - Bottom)` 和 `Y = Left - x*(Left - Right)`。LootCollector 区域 ID 满足 `z = WorldMapArea ID + 1`。转换使用飞升采集的 WMA 边界。用 32,485 条导出的生成点验证，误差中位数为 1.4–1.7 码，与来源仅保留 1 位小数的精度相符。
- 汇总表沿用 Discord 分析报告的去重规则：同一物品在同一区域内，相距不超过 0.005 地图单位的点位合并。
- 在有场景物件数据的地图里，ZIP 存档的 4,108 个点位中有 1,548 个在 5 码内能找到导出的场景物件。记录缺少物品与具体物件类型的对应关系。

## 覆盖范围

| 服务器地图 | 点位数 |
|---|---:|
| 0 东部王国 | 2,939 |
| 1 卡利姆多 | 2,243 |
| 530 外域 | 65 |
| 副本（19 张地图，例如 189、329、36、429、47） | 约 450 |
| **诺森德** | **0** |
| **Pale Reach** | **0** |

## 数据来源与可信度

| 来源 | 内容 | 使用依据 |
|---|---|---|
| 客户端内的 `LootCollector_StarterDB` v7.0（2026-08-20 文件夹） | 1,970 个点位 / 1,600 个物品 | 随客户端附带的公开插件数据，用作基础数据。 |
| Discord 玩家分享的 LootCollector SavedVariables（3 个 ZIP 和 6 个 RAR） | 分别新增 1,125 / 2,608 个点位，以及 155 / 218 个物品 | 来自玩家的实际记录。原文件包含发现者姓名，本项目只读取数值字段。 |
| db.exil.es 镜像（基准日期 2026-08-29） | 7 档升级表、S1 物品等级和拾取位置 | 按网页内容尽量还原。1,849 个名称中有 1,230 个关联多个基础档 ID，有 9 条升级链在不同档次重复使用同一 ID。13,953 个页面中有 2,289 个与 S1 的物品等级不同，以 S1 为准。 |
| LootCollector 的 `WorldforgedUpgrades.lua`（经 Lootsmith 提取） | 1,978 条按 ID 整理的升级链 | 用于确认各档 ID，实际使用前与按名称整理的升级表核对。 |
| Bisbeard 社区地图（经 Lootsmith 提取） | 1,481 个物品在 49 个区域的点位 | 社区资料，可作为旁证。 |
| S1 物品缓存（`hertigservices/ascension-data`） | 全部 13,953 个世界铸造 ID 的物品数据和物品等级 | 本项目用于确认物品数据的依据。 |
| `ItemVariationData.json`（客户端 `Data/Content`，3.8 MB） | 普通、英雄、血铸和史诗变体 | 普通档没有世界铸造基础物品。史诗档数组与初步提取的 725 个世界铸造 ID、与本项目汇总的 1,244 个 ID 存在冲突。应避免直接导入这些史诗档数组。 |
| 整合包的世界数据库 | 自定义掉落和商人记录均为 0 | 没有提供可用的相关记录。 |
| 25 个 Worldforged Cache 坐标（地图 0 有 10 个，地图 1 有 15 个） | 场景物件的位置 | 其中 10 个有宝箱模板，15 个没有。导出缺少掉落表，实际拾取位置见 `DISCORD-DUMP-VERDICT.md` 第 2.1 节的分析。 |

## 数据缺口

- **高度 Z**。可通过地形为约 63% 的点位估算高度，约 21% 的估算误差超过 10 码。
- **实际生成点和物件类型**。点位只记录玩家拾取时的位置，无法确定物品来自袋子、武器还是尸体等物件。
- **随机词缀的具体数值**。据 Lootsmith 在 2026 年 8 月 22 日的核对，Bisbeard 的 13,951 条带词缀物品记录均缺少词缀文本行，具体数值需在游戏内查看。
- **掉落与拾取概率**。现有来源没有测量结果，Exiles 的 `Observed` 列在所有行中均为 0。
- **服务器端的升级机制和 NPC 行为**。现有升级表只记录各档物品对应关系。
- **诺森德和 Pale Reach**。所有来源均无点位。

## 隐私

原始 LootCollector 记录包含发现者、发起者和投票者姓名。公开数据已移除这些信息。解码器只读取 `dt, i, z, x, y` 数值字段。提交前使用 `leak_check2` 扫描了所有文件，检查范围包含 2,723 个已知姓名值和账号、角色文件夹名称。请勿将原始 SavedVariables 提交到此仓库。

## 统计核对

- 点位汇总与 `DISCORD-DUMP-VERDICT.md` 第 9 节一致：1,970 + 1,125 + 2,608 = **5,703 个点位**。1,600 + 155 + 218 = **1,973 个物品**，名称均取自 S1。
- 升级表与 `exiles-loot-quests.md` 第 8 节一致：13,953 个 ID、1,849 个名称、1,787 条完整升级链，全部 13,953 个 ID 都有 S1 物品等级。60 级、ZG、MC、BWL、AQ40、Naxx 档的物品等级增幅中位数依次为 +4、+10、+13、+18、+21 和 +28。

## 与 SUNDERBORN 计划的关系

- **AD5 / DA5，2 号服务器的世界铸造升级**：先用本仓库的两份升级表核对并建立查询表，再实现升级 NPC。
- 每个新增物品 ID 都需要在客户端 `Item.dbc` 中添加一行，否则装备后无法显示（AD7）。
- 拾取物件的生成点无法按职业限制。若世界铸造物件只在 2 号服务器出现，需要使用位面机制或该服专用地图。
- 档次解锁可沿用已启用的 `mod-individual-progression`，对应 MC、BWL、AQ40 和 Naxx。

## 相关文档

- [点位分析报告](docs/DISCORD-DUMP-lootcollector-lens.md)
- [隐私检查记录](PRIVACY-GATE.md)
- [数据文件与字段说明](data/README.md)
