---
name: superpowers
description: Superpowers 是一個 AI Agent 軟體開發方法論，包含 composable skills、測試驅動開發、計畫驅動執行。當用戶需要：(1) 了解 Superpowers、(2) 軟體開發流程、(3) TDD、(4) 建立技能。
---

# Superpowers Skill

## 簡介

[Superpowers](https://github.com/obra/superpowers) 是 AI Agent 的軟體開發方法論。

## 核心哲學

- **TDD** - 先寫測試再寫 code
- **系統化** - 流程優先於猜測
- **化繁為簡** - 簡單為首要目標
- **驗證為準** - 確認後才算成功

## 工作流程

1. **brainstorming** - 需求確認與設計驗證
2. **using-git-worktrees** - 建立隔離工作區
3. **writing-plans** - 拆解成小任務（2-5 分鐘/個）
4. **executing-plans/subagent-driven-development** - 子代理執行 + 兩階段審查
5. **test-driven-development** - RED-GREEN-REFACTOR 循環
6. **requesting-code-review** - 程式碼審查
7. **finishing-a-development-branch** - 完成分支

## 內建 Skills

| 類別 | Skills |
|------|--------|
| **測試** | test-driven-development |
| **除錯** | systematic-debugging, verification-before-completion |
| **協作** | brainstorming, writing-plans, requesting-code-review, using-git-worktrees |
| **Meta** | writing-skills, using-superpowers |

## 使用原則

- 每個任務前檢查相關 skill
- 強制執行，不是建議
- 任務要有精確檔案路徑和驗證步驟

## 詳細文檔

參考 `references/README.md`