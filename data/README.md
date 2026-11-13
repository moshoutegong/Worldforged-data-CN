# 数据文件与字段说明

查某件物品的坐标，请用 [点位总表](wf_pins_union.csv) 搜索 `item_id`。统计每件物品收录了多少位置，请看 [物品汇总表](wf_items_union.csv)。按升级档次查物品 ID，请看 [Exiles 升级表](exiles_wf_ladder.csv)。

这些文件来自飞升历史存档。点位是玩家拾取时的站位，跨服使用时应现场核对。数据的来源、误差及隐私处理见[点位分析报告](../docs/DISCORD-DUMP-lootcollector-lens.md)和[隐私检查记录](../PRIVACY-GATE.md)。

## 点位总表

每行代表一个物品在一个区域内的拾取点位，同一 `item_id` 可以出现多行。

| 字段 | 含义 |
|---|---|
| `item_id` / `item_name` | 物品 ID / 原始英文名称。关联表时优先使用 ID |
| `s1_item_level` / `s1_required_level` | S1 缓存中的物品等级 / 所需角色等级 |
| `lc_z` | LootCollector 区域 ID |
| `wma_id` / `wma_name` | WorldMapArea ID / 区域内部名称。`lc_z = wma_id + 1` |
| `server_map` | 服务器地图 ID，例如 0 是东部王国、1 是卡利姆多、530 是外域 |
| `norm_x` / `norm_y` | 区域地图上的 0–1 比例坐标。游戏里按百分比显示时乘以 100，例如 `0.3545` 对应 `35.45` |
| `server_X` / `server_Y` | 用飞升采集的地图边界换算出的服务器平面坐标，单位为码 |
| `in_starterdb` / `in_dump_zip` / `in_dump_rar` | 是否来自插件初始库、玩家 ZIP 或玩家 RAR。1 表示该来源有记录，0 表示没有 |
| `n_records` | 汇入这一点位的记录数。多个玩家存档可能同步过同一条记录，因此该值无法直接视作独立实测次数 |

## 物品汇总表

每个 `item_id` 一行。`n_pins` 是去重后的点位总数。`n_pins_starterdb`、`n_pins_dump_zip`、`n_pins_dump_rar` 是各来源覆盖的点位数，同一个点位可以出现在多个来源。`server_maps` 和 `zones` 列出该物品的地图和区域。

## Exiles 升级表

| 字段 | 含义 |
|---|---|
| `name` | 用于归组升级链的物品名称 |
| `tier` / `tier_label` | 升级档次及其标签 |
| `item_id` | 对应档次的物品 ID |
| `s1_item_level` / `s1_required_level` | S1 物品等级 / 所需角色等级 |
| `found_at_zone` | Exiles 页面保留的拾取位置文本，可能同时包含区域名和坐标 |
| `name_has_all_7_tiers` | 该名称是否收录完整 7 档，1 为齐全，0 为不齐全 |

[地图边界表](worldmaparea_bounds_captured.csv)用于坐标换算。[lootsmith/](lootsmith/) 存放社区地图、世界铸造标记和升级链 JSON。[provenance/](provenance/) 保留 ZIP 来源的提取结果，适合追查数据出处。

## 中文对照表

| 文件 | 关联方式与范围 |
|---|---|
| [地图名对照](zone_names_zhCN.csv) | 按 `wma_id` 关联采集的地图边界。优先沿用 AscensionCN 的地图译名，再查 LootCollector。其余地图名标为「地图暂译」，内部代号保留用于查询。 |
| [物品名对照](item_names_zhCN.csv) | 覆盖物品汇总表和 Exiles 升级表的物品 ID。优先按 ID 查 AscensionCN，再用该插件的英文词典精确匹配名称。其余沿用同名物品的 AscensionCN 参考译名，或补入人工和机器暂译。来源标在 `translation_source`。暂译尚未逐条在 ArdenWoW 验证。 |
| [社区地图拾取备注](atlas_pickup_notes_zhCN.csv) | 仅收录 Bisbeard 地图中有备注的世界铸造标记。`marker_index` 从 0 开始，对应原 JSON 的 `markers` 数组下标。`zone_index` 对应该 JSON 的 `zones` 数组。表内附有地图和物品的中文对照。拾取物件保留英文关键词，便于在英文客户端辨认。 |

中文表使用 UTF-8，保留英文名称、物品 ID、区域 ID 和原始坐标。物品名和地图名的 `translation_source` 标注所用的译名来源。社区地图里的位置和物件名称来自历史记录，可能有截断或误差。

