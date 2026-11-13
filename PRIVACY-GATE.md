# 隐私检查记录

**简体中文** · [English](PRIVACY-GATE.en.md)

上游作者在 2026 年 9 月 11 日首次提交前，对当时的 35 份 CSV、JSON、Markdown 和 Python 文件进行了检查。

## 姓名检查

`leak_check2` 比对了 LootCollector SavedVariables 中的 2,723 个姓名值，以及两批 Discord 备份里的账号和角色目录名。插件键名类别 `[lc-key]` 另经过游戏词汇筛选。

- 命中 15 行，全部属于 `[lc-key]`。账号 `[acct]` 和角色 `[char]` 两类均为 0。
- 15 次命中来自两项。物品名 **Signet of …'kes** 在 7 个文件中出现 13 次。S1 物品缓存确认，物品 354251 及其升级链的 8 个 ID 都属于护甲（类型 4），物品等级分别为 48、60、64、70、73、77、81、88。
- 另外 2 次命中来自来源地址 `coa.bisbeard.com/atlas/atlas.json` 中的路径词 `atlas`。

两项都通过核查，无需遮盖。

## 凭据、邮箱和其他用户目录检查

没有文件触发警报。检查未发现邮箱地址、其他 Windows 用户的目录、疑似私钥或凭据。

## 提交要求

请勿向仓库提交原始 LootCollector SavedVariables，其中含有发现者、发起者和投票者姓名。`tools/` 下的解码器只读取 `dt, i, z, x, y` 数值字段。
