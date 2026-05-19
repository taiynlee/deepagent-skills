---
name: postgres
description: PostgreSQL 資料庫工具。支援查詢、CRUD、資料庫管理。當用戶需要：(1) 查詢資料庫、(2) CRUD 操作、(3) 資料庫管理任務。
---

# PostgreSQL 工具 (postgres)

## 環境設定

請在 `.env` 檔案中設定以下變數：

```bash
DB_HOST=your-database-host
DB_PORT=5432
DB_USER=your-username
DB_NAME=your-database-name
DB_PASSWORD=your-password
```

## 執行方式

使用 Docker + postgres:15 鏡像執行 psql 命令。

### 查詢

```bash
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "SELECT * FROM student LIMIT 10"
```

### 統計

```bash
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "SELECT COUNT(*) FROM student"
```

### 新增

```bash
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "INSERT INTO student (name, age) VALUES ('Tommy', 30)"
```

### 修改

```bash
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "UPDATE student SET name='NewName' WHERE id=1"
```

### 刪除

```bash
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  -c "DELETE FROM student WHERE id=5"
```

## 管理指令

```bash
# 列出所有資料表
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt"

# 查看錶結構
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d student"

# 查看 schema
docker run --rm -e PGPASSWORD=$DB_PASSWORD postgres:15 \
  psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dn"
```

## 常用 SQL 範例

| 任務 | SQL |
|------|-----|
| 查詢所有資料 | `SELECT * FROM student` |
| 統計筆數 | `SELECT COUNT(*) FROM student` |
| 條件查詢 | `SELECT * FROM student WHERE age > 20` |
| 新增資料 | `INSERT INTO student (name, age) VALUES ('John', 25)` |
| 修改資料 | `UPDATE student SET name='Mary' WHERE id=1` |
| 刪除資料 | `DELETE FROM student WHERE id=3` |