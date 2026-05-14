---
name: pg-query
description: PostgreSQL 自然語言查詢工具。當用戶需要：(1) 用自然語言查詢資料庫、(2) 新增、修改、刪除資料庫資料、(3) 描述資料庫結構、(4) 執行任何 SQL 操作。透過 LLM 將自然語言轉換為 SQL 並執行。
---

# PostgreSQL Natural Language Query

透過自然語言操作 PostgreSQL 資料庫。

## 環境變數設定

```bash
export PG_HOST=localhost
export PG_PORT=5432
export PG_DATABASE=mydb
export PG_USER=myuser
export PG_PASSWORD=mypassword
export OPENAI_API_KEY=sk-...  # OpenAI API key
```

## 使用方式

```bash
pg-query "<自然語言描述>"
```

## 操作範例

| 任務 | 自然語言 |
|------|---------|
| 查詢 | "找出所有年齡大於 30 歲的用戶" |
| 新增 | "在 users 表新增一筆記錄，name 是 John，email 是 john@example.com" |
| 修改 | "將 users 表中 id 為 5 的記錄的 email 更新為 new@example.com" |
| 刪除 | "刪除 orders 表中日期在 2024-01-01 之前的訂單" |
| 統計 | "計算每個產品的總銷售額" |

## 指令

- `--table <name>`: 指定主要操作的資料表
- `--limit <n>`: 限制查詢結果筆數（預設 10）
- `--dry-run`: 只顯示 SQL，不執行
- `--describe`: 顯示資料表結構
- `--schema`: 顯示整個資料庫的 schema

## 輸出格式

指令會輸出：
1. 轉換後的 SQL 語句
2. 執行結果（格式化表格）
3. 影響的資料列數（如有）

## 腳本位置

執行時使用：`~/.deepagents/agent/skills/pg-query/scripts/pg_query.py`