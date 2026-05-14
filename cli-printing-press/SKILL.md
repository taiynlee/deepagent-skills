---
name: cli-printing-press
description: CLI 生成工具。將任意 API 或網站轉換成 AI Agent 原生的 Go CLI + MCP Server。當用戶需要：(1) 把某個服務或網站變成 CLI、(2) 生成新的 CLI 工具、(3) 自動化重複性工作、(4) 查詢 printing-press library 中的現有 CLI、(5) 了解如何用 printing-press 生成 CLI。
---

# CLI Printing Press

將 API 或網站轉換成生產級 CLI 的工具。

## 快速查詢現有 CLI

可用工具列表（87 個）：

| 類別 | CLI | 用途 |
|------|-----|------|
| 體育 | `espn` | ESPN 比分、統計、新聞 |
| 旅遊 | `flight-goat` | 機票搜尋（Google Flights + Kayak） |
| 旅遊 | `airbnb` | Airbnb 房源搜尋 |
| 金融 | `stripe` | Stripe 支付管理 |
| 金融 | `mercury` | 商業銀行 API |
| 金融 | `coingecko` | 加密貨幣數據 |
| 行銷 | `dub` | 短連結管理 |
| 行銷 | `klaviyo` | 郵件營銷自動化 |
| 生產力 | `linear` | 專案管理 |
| 生產力 | `notion` | 文件資料庫 |
| 生產力 | `slack` | 訊息管理 |
| 生產力 | `jira` | 任務追蹤 |
| 美食 | `dominos` | 披薩訂購 |
| 美食 | `instacart` | 生鮮外送 |
| 美食 | `recipe-goat` | 食譜搜尋 |
| 監控 | `sentry` | 錯誤追蹤 |
| 開發 | `github` | GitHub API |
| 開發 | `docker-hub` | 容器鏡像 |
| 開發 | `pypi` | Python 包查詢 |

## 安裝現有 CLI

```bash
# 安裝單一工具
npx -y @mvanhorn/printing-press install espn

# 安裝 starter pack（espn, flight-goat, movie-goat, recipe-goat）
npx -y @mvanhorn/printing-press install starter-pack

# 搜尋工具
npx -y @mvanhorn/printing-press search sports

# 更新工具
npx -y @mvanhorn/printing-press update espn
```

## 生成新 CLI

若要為新 API/網站生成 CLI，需要使用 **CLI Printing Press** 本身：

### 前置需求
- Go 1.26.3+
- Claude Code（用於 slash command）
- GitHub token

### 生成流程
```bash
# 1. 安裝 printing-press
go install github.com/mvanhorn/cli-printing-press/v4/cmd/printing-press@latest

# 2. 安裝 skill
gh skill install mvanhorn/cli-printing-press --agent claude-code --scope user

# 3. 在 Claude Code 中使用
/printing-press <API名稱或URL>
```

### 支援的輸入模式
| 模式 | 用法 |
|------|------|
| OpenAPI spec | `--spec ./openapi.yaml` |
| HAR 檔案 | `--har ./capture.har` |
| 網站 URL | `https://example.com/api` |

## 工作流程

當用戶想把某個工作變成 CLI 時：

1. **先查詢是否已有**：檢查 printing-press-library 是否已有相關 CLI
2. **若無，評估可行性**：
   - 有無 OpenAPI spec → 可直接生成
   - 有無公開網站 → 可用瀏覽器嗅探
   - 需手動建立 spec → 較複雜，需更多時間
3. **說明生成成本**：一般需要 30-60 分鐘，視複雜度而定
4. **引導用戶**：告知需自行運行 `/printing-press`（因需 Claude Code）

## 現有 CLI 快速使用

```
espn <查詢>                    # 體育查詢
flight-goat <起點> to <終點>   # 機票搜尋
stripe charges list            # 查詢交易
linear issues --status open    # 查看 issue
notion database query <id>     # 查詢資料庫
```

## 限制

- 此 skill 本身不直接運行 `/printing-press`（需 Claude Code）
- 生成新 CLI 需要用戶本機有 Go 和 Claude Code 環境
- 某些 API 需要付費或認證