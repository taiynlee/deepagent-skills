---
name: find-skills
description: Skills 工具用於搜尋、安裝、管理 AI Agent skills。當用戶需要：(1) 搜尋 AI Agent skills、(2) 查詢可用 skills、(3) 安裝或管理 skills、(4) 了解 vercel-labs/skills。
---

# Find Skills Skill

## 簡介

[vercel-labs/skills](https://github.com/vercel-labs/skills) 是跨 Agent 的 Skills 管理 CLI。

## 快速使用

```bash
# 安裝 skills
npx skills add vercel-labs/agent-skills

# 列出可用 skills
npx skills add vercel-labs/agent-skills --list

# 搜尋 skills
npx skills find [關鍵字]

# 更新 skills
npx skills update

# 移除 skills
npx skills remove [name]
```

## 安裝特定 Skill

```bash
# 安裝特定 skill
npx skills add vercel-labs/agent-skills --skill frontend-design

# 安裝到特定 agent
npx skills add vercel-labs/agent-skills -a claude-code -a opencode

# 全域安裝
npx skills add vercel-labs/agent-skills -g
```

## 支援的 Agents

支援 56 種 Agent，包含：
- Claude Code、Codex、Cursor、OpenCode
- OpenHands、Cline、GitHub Copilot
- Deep Agents、Gemini CLI、Windsurf、Trae

## Skill 格式

```markdown
---
name: my-skill
description: 說明這個 skill 做什麼
---
# My Skill
... instructions ...
```

## 發現更多 Skills

- [skills.sh](https://skills.sh) - Skills 目錄
- [Agent Skills Specification](https://agentskills.io)