# 工具使用说明

只查询世界铸造的物品、地图和坐标时，可以直接打开 [CSV 与中文对照表](../data/README.md)。

| 脚本 | 用途 | 需要的输入 |
|---|---|---|
| [build_pin_union.py](build_pin_union.py) | 重新生成点位总表和物品汇总表 | LootCollector 初始库、玩家 ZIP / RAR、WMA 边界缓存、S1 物品缓存和原工作目录中的辅助模块。读取 RAR 需要 7-Zip |
| [build_exiles_ladder.py](build_exiles_ladder.py) | 重建按名称归组的升级表 | Exiles 物品镜像数据和 S1 物品缓存 |
| [luasv.py](lootcollector-decoder/luasv.py) | 将 SavedVariables 作为 Lua 表文本解析 | 可在自己的 Python 脚本中导入 `parse_sv`，输入字符串，不执行 Lua |
| [starterdecode.py](lootcollector-decoder/starterdecode.py) | 解码初始库的 `!LC1!` 数据 | 本地 LootCollector_StarterDB 的 `db.lua` |
| [lootcollector-decoder/](lootcollector-decoder/) 其他脚本 | 读取备份、转换坐标、统计点位及检查隐私字段 | 原报告对应的输入存档及中间缓存。详见[分析步骤](../docs/DISCORD-DUMP-lootcollector-lens.md#11-分析步骤) |

这些是上游保留的研究脚本。部分脚本写死了作者的 Windows 目录，例如 `dumpio.py` 中的 `ROOT`、生成脚本中的 `SP`，以及解码工具中的 `SRC`、`OUT`。复现前需准备所需输入并修改路径。报告里的 `Account.zip` 等原始备份未随仓库发布。运行生成脚本前请确认输出目录，以免覆盖已有 CSV。请勿上传包含玩家姓名的原始 SavedVariables。[隐私检查记录](../PRIVACY-GATE.md)
