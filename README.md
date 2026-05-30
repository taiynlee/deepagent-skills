# deepagent-skills

深度 AI Agent 技能集合（Deep Agents CLI 專用）。涵蓋資料庫管理、Kubernetes、Gmail、API 查詢、CLI 工具生成與開發方法論。

## 技能列表

| 技能 | 說明 |
|------|------|
| [cli-printing-press](#cli-printing-press) | 將 API 或網站轉換成生產級 CLI + MCP Server |
| [find-skills](#find-skills) | 搜尋、安裝、管理 AI Agent Skills |
| [gmail-read](#gmail-read) | 讀取 Gmail 最新郵件 |
| [k8s-admin](#k8s-admin) | Kubernetes 集群日常管理 |
| [postgres](#postgres) | PostgreSQL 查詢與管理（Docker 執行） |
| [public-apis](#public-apis) | 查詢免費公開 API 目錄 |
| [superpowers](#superpowers) | AI Agent 軟體開發方法論 |

---

## cli-printing-press

將任意 API 或網站轉換成 AI Agent 原生的 Go CLI + MCP Server。

**觸發時機：**
- 把某個服務或網站變成 CLI
- 查詢 printing-press library 中的現有 CLI（共 87 個）
- 了解如何用 printing-press 生成 CLI

**安裝現有 CLI：**
```bash
# 安裝單一工具
npx -y @mvanhorn/printing-press install espn

# 搜尋工具
npx -y @mvanhorn/printing-press search sports

# 更新工具
npx -y @mvanhorn/printing-press update espn
```

**生成新 CLI（需 Go 1.26.3+ 與 Claude Code）：**
```bash
# 1. 安裝 printing-press
go install github.com/mvanhorn/cli-printing-press/v4/cmd/printing-press@latest

# 2. 安裝 skill
gh skill install mvanhorn/cli-printing-press --agent claude-code --scope user

# 3. 在 Claude Code 中觸發
/printing-press <API名稱或URL>
```

**已收錄 CLI 分類（共 87 個）：**

| 類別 | 工具範例 |
|------|---------|
| 體育 | `espn` |
| 旅遊 | `flight-goat`, `airbnb` |
| 金融 | `stripe`, `mercury`, `coingecko` |
| 生產力 | `linear`, `notion`, `slack`, `jira` |
| 開發 | `github`, `docker-hub`, `pypi`, `sentry` |

---

## find-skills

搜尋與管理跨 Agent 的 Skills 生態系（基於 [vercel-labs/skills](https://github.com/vercel-labs/skills)）。

**觸發時機：** 搜尋/安裝/管理/更新 AI Agent skills。

**常用指令：**
```bash
# 安裝 skills
npx skills add vercel-labs/agent-skills

# 列出可用 skills
npx skills add vercel-labs/agent-skills --list

# 安裝特定 skill 到特定 agent
npx skills add vercel-labs/agent-skills --skill frontend-design -a claude-code

# 全域安裝
npx skills add vercel-labs/agent-skills -g

# 更新
npx skills update

# 移除
npx skills remove [name]
```

**支援 56 種 Agent**，包含 Claude Code、Codex、Cursor、OpenCode、Gemini CLI、GitHub Copilot 等。

---

## gmail-read

使用 Google OAuth2 讀取 Gmail 最新郵件。

**前置需求：** `.env` 檔需包含：
```
GOOGLE_REFRESH_TOKEN=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

**執行方式（Python）：**
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri='https://oauth2.googleapis.com/token',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)
service = build('gmail', 'v1', credentials=creds)
results = service.users().messages().list(userId='me', maxResults=1).execute()
```

**依賴套件：** `google-api-python-client`, `google-auth`

---

## k8s-admin

Kubernetes 集群日常管理工具，涵蓋資源查詢、describe、logs。

**觸發時機：** 列出資源、查看 Pod 詳情、查看 logs、進入 Pod。

**常用指令：**

```bash
# 列出資源
kubectl get ns                            # Namespaces
kubectl get nodes                         # Nodes
kubectl get all --all-namespaces          # 所有 Namespaced 資源
kubectl get pods -n <namespace>           # Pods
kubectl get svc -n <namespace>            # Services
kubectl get deploy -n <namespace>         # Deployments
kubectl get secret -n <namespace>         # Secrets
kubectl get ingress -n <namespace>        # Ingresses

# 詳細資訊
kubectl describe pod <name> -n <namespace>
kubectl describe deploy <name> -n <namespace>

# Logs
kubectl logs <name> -n <namespace>
kubectl logs <name> -n <namespace> --tail 100
kubectl logs <name> -n <namespace> -f       # 即時追蹤

# 進入 Pod
kubectl exec -it <name> -n <namespace> -- /bin/bash
```

---

## postgres

透過 Docker 執行 psql 操作 PostgreSQL，無需本機安裝。

**環境設定（`.env`）：**
```bash
DB_HOST=your-database-host
DB_PORT=5432
DB_USER=your-username
DB_NAME=your-database-name
DB_PASSWORD=your-password
```

**查詢範例：**
```bash
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "SELECT * FROM table LIMIT 10"
```

**CRUD 快速參考：**

| 操作 | SQL |
|------|-----|
| 查詢 | `SELECT * FROM table WHERE id = 1` |
| 新增 | `INSERT INTO table (col) VALUES ('val')` |
| 修改 | `UPDATE table SET col='val' WHERE id=1` |
| 刪除 | `DELETE FROM table WHERE id=1` |
| 列出表 | `\dt` |
| 查看結構 | `\d tablename` |

---

## public-apis

查詢 [public-apis/public-apis](https://github.com/public-apis/public-apis)——社群維護的免費公開 API 目錄。

**觸發時機：** 查詢某類 API、找免費 API 資源。

**查詢方式：**
```bash
# 查看完整清單
curl -s "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md"

# 搜尋特定類別
curl -s "https://raw.githubusercontent.com/public-apis/public-apis/master/README.md" \
  | grep -i -B1 -A1 "finance"
```

**常用分類關鍵字：**
`stock` / `finance` / `weather` / `crypto` / `train` / `railway` / `forex`

**本地快取自動更新（cron）：**
```bash
# 每天凌晨 3 點更新
(crontab -l 2>/dev/null; echo "0 3 * * * ~/.deepagents/agent/skills/public-apis/scripts/update.sh") | crontab -
```

---

## superpowers

AI Agent 完整軟體開發方法論，讓 Agent 自動遵循 TDD、計畫驅動、子代理執行流程。

**核心哲學：** TDD → 計畫 → 子代理執行 → 審查 → 驗證

**完整工作流程：**

| 步驟 | Skill | 說明 |
|------|-------|------|
| 1 | `brainstorming` | 需求確認與設計驗證 |
| 2 | `using-git-worktrees` | 建立隔離工作區 |
| 3 | `writing-plans` | 拆解任務（每個 2-5 分鐘） |
| 4 | `subagent-driven-development` | 子代理執行 + 兩階段審查 |
| 5 | `test-driven-development` | RED → GREEN → REFACTOR |
| 6 | `requesting-code-review` | 程式碼審查 |
| 7 | `finishing-a-development-branch` | 完成分支 |

**內建 Skills 清單：**

| 類別 | Skills |
|------|--------|
| 測試 | `test-driven-development` |
| 除錯 | `systematic-debugging`, `verification-before-completion` |
| 計畫 | `brainstorming`, `writing-plans`, `executing-plans` |
| 協作 | `requesting-code-review`, `receiving-code-review` |
| 工作區 | `using-git-worktrees`, `using-superpowers` |
| Meta | `writing-skills`, `dispatching-parallel-agents` |

詳細文件：[obra/superpowers](https://github.com/obra/superpowers)

---

## 安裝方式

```bash
# 安裝全部 skills（Deep Agents CLI）
da skills install taiynlee/deepagent-skills

# 安裝特定 skill
da skills install taiynlee/deepagent-skills --skill k8s-admin
```
