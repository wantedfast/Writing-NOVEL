# Writing-NOVEL

一个用于原创中文小说写作、续写和润色的 Codex Skill。它参考《龙族》1—4 部时期的叙事机制，侧重人物观察、电影感场景调度与情绪节奏；不包含原作全文，也不用于复用原作人物、世界观或情节。

## 安装

在 PowerShell 中，将仓库克隆到个人 Skill 目录：

```powershell
git clone https://github.com/wantedfast/Writing-NOVEL.git "$env:USERPROFILE\.codex\skills\jiangnan-fiction-general"
```

如目标目录已存在，请先自行比较或备份现有内容，不要直接覆盖。安装后可在 Codex 中使用 `$jiangnan-fiction-general`。

入口说明见 [SKILL.md](SKILL.md)。`references/` 按写作场景选择性读取；`scripts/audit_style.py` 只用于辅助检查表层节奏，不能替代文学判断。
