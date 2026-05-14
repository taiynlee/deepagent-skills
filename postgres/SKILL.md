---
name: postgres
description: PostgreSQL 資料庫工具。支援自然語言查詢與 CRUD、資料庫管理、效能監控。當用戶需要：(1) 自然語言查詢資料庫、(2) CRUD 操作、(3) 資料庫管理任務、(4) 效能監控與優化。
---

# PostgreSQL 工具 (postgres)

整合查詢與管理功能於一體。

## 環境變數

已預設為你的環境（tommy 資料庫）：
- HOST: active.aiengineerdev.service.paas.wistron.com
- PORT: 15237
- USER: dxlab
- DATABASE: tommy

## 腳本位置

- 查詢/CRUD: `~/.deepagents/agent/skills/postgres/scripts/pg_query.py`
- 管理監控: `~/.deepagents/agent/skills/postgres/scripts/pg_admin.py`

## 自然語言查詢

```bash
python3 scripts/pg_query.py "找出所有 student 表的資料"
python3 scripts/pg_query.py "統計 student 表的筆數"
python3 scripts/pg_query.py "在 student 表新增 name=Tommy, age=25"
```

## 管理指令

```bash
# 列出所有資料表
python3 scripts/pg_admin.py --list-tables

# 查看資料庫大小
python3 scripts/pg_admin.py --db-size

# 查看慢查詢
python3 scripts/pg_admin.py --slow-queries

# 查看活躍連線
python3 scripts/pg_admin.py --active-connections

# 健康檢查
python3 scripts/pg_admin.py --health-check
```

## 常用查詢範例

| 任務 | 自然語言 |
|------|---------|
| 統計筆數 | "統計 student 表的筆數" |
| 查詢條件 | "找出 age > 20 的 student" |
| 新增資料 | "在 student 表新增 name=John" |
| 修改資料 | "將 student 表 id=1 的 name 更新為 Mary" |
| 刪除資料 | "刪除 student 表中 id=5 的資料" |

## SQL 直接執行

```bash
# 只顯示 SQL 不執行
python3 scripts/pg_query.py "SELECT * FROM student" --dry-run

# 顯示錶結構
python3 scripts/pg_query.py --describe student

# 顯示整個 schema
python3 scripts/pg_query.py --schema
```