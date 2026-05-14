#!/usr/bin/env python3
"""
PostgreSQL Natural Language Query Tool
透過 OpenAI 將自然語言轉換為 SQL 並執行
"""

import os
import sys
import json
import argparse
import re
from typing import Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("請先安裝 psycopg2-binary: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)


def get_db_connection():
    """建立資料庫連線"""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        database=os.getenv("PG_DATABASE", "postgres"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", ""),
        cursor_factory=RealDictCursor
    )


def get_table_schema(table_name: Optional[str] = None) -> str:
    """取得資料表結構"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if table_name:
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
    else:
        cur.execute("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return json.dumps(rows, indent=2, default=str)


def generate_sql(nl_query: str, table_name: Optional[str] = None, openai_key: Optional[str] = None) -> str:
    """使用 OpenAI 將自然語言轉換為 SQL"""
    api_key = openai_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "-- 錯誤: 請設定 OPENAI_API_KEY 環境變數"
    
    # 取得 schema
    schema = get_table_schema(table_name)
    
    # 建立 prompt
    prompt = f"""將以下自然語言轉換為 PostgreSQL SQL 語句。只輸出 SQL，不要其他解釋。

可用資料表結構:
{schema}

自然語言查詢: {nl_query}

SQL:"""

    import urllib.request
    import urllib.error
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "你是一個 SQL 專家。只能輸出 SQL 語句，不要有任何其他文字。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0
    }
    
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            return result["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        return f"-- API 錯誤: {e.code} - {e.read().decode()}"
    except Exception as e:
        return f"-- 錯誤: {str(e)}"


def execute_sql(sql: str) -> tuple:
    """執行 SQL 並回傳結果"""
    # 清理 SQL（移除可能的 markdown 格式）
    sql = re.sub(r'^```sql\s*', '', sql)
    sql = re.sub(r'^```\s*', '', sql)
    sql = sql.strip().rstrip(';')
    
    if not sql or sql.startswith("--"):
        return [], sql, "無有效 SQL"
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(sql)
        
        # 判斷是查詢還是修改
        if cur.description:
            rows = cur.fetchall()
            conn.commit()
            return rows, sql, f"查到 {len(rows)} 筆記錄"
        else:
            rows = cur.rowcount
            conn.commit()
            return [], sql, f"影響 {rows} 筆記錄"
            
    except Exception as e:
        conn.rollback()
        return [], sql, f"執行錯誤: {str(e)}"
    finally:
        cur.close()
        conn.close()


def format_results(rows: list) -> str:
    """格式化輸出結果"""
    if not rows:
        return ""
    
    if isinstance(rows[0], dict):
        headers = list(rows[0].keys())
        col_widths = {h: max(len(str(h)), max(len(str(r.get(h, ""))) for r in rows)) for h in headers}
        
        # 表頭
        header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
        separator = "-+-".join("-" * col_widths[h] for h in headers)
        
        # 資料列
        data_lines = []
        for row in rows:
            line = " | ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers)
            data_lines.append(line)
        
        return "\n".join([header_line, separator] + data_lines)
    
    return "\n".join(str(r) for r in rows)


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL Natural Language Query")
    parser.add_argument("query", nargs="?", help="自然語言查詢")
    parser.add_argument("--table", "-t", help="指定資料表")
    parser.add_argument("--limit", "-l", type=int, default=10, help="結果筆數限制")
    parser.add_argument("--dry-run", "-d", action="store_true", help="只顯示 SQL")
    parser.add_argument("--describe", action="store_true", help="顯示資料表結構")
    parser.add_argument("--schema", "-s", action="store_true", help="顯示資料庫 schema")
    parser.add_argument("--api-key", help="OpenAI API Key")
    
    args = parser.parse_args()
    
    # 描述模式
    if args.describe and args.table:
        schema = get_table_schema(args.table)
        print(f"=== {args.table} 結構 ===")
        data = json.loads(schema)
        for col in data:
            nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col["column_default"] else ""
            print(f"  {col['column_name']:20} {col['data_type']:20} {nullable}{default}")
        return
    
    # Schema 模式
    if args.schema:
        schema = get_table_schema()
        data = json.loads(schema)
        tables = {}
        for row in data:
            t = row["table_name"]
            if t not in tables:
                tables[t] = []
            tables[t].append(f"    {row['column_name']}: {row['data_type']}")
        
        print("=== 資料庫 Schema ===")
        for t, cols in tables.items():
            print(f"\n{t}")
            print("\n".join(cols))
        return
    
    # 一般查詢
    if not args.query:
        print("請提供自然語言查詢")
        return
    
    # 加上 LIMIT
    nl_with_limit = args.query
    if args.limit and args.limit > 0:
        nl_with_limit += f" (limit {args.limit})"
    
    # 產生 SQL
    sql = generate_sql(nl_with_limit, args.table, args.api_key)
    
    if args.dry_run:
        print(sql)
        return
    
    # 執行
    rows, _, msg = execute_sql(sql)
    print(f"-- SQL: {sql}")
    print(f"-- {msg}")
    
    if rows:
        print("\n" + format_results(rows))


if __name__ == "__main__":
    main()