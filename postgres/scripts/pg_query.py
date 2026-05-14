#!/usr/bin/env python3
"""
PostgreSQL Natural Language Query Tool
透過 OpenAI 將自然語言轉換為 SQL 並執行
支援：查詢、新增、修改、刪除、建立資料表等
"""

import os
import sys
import json
import argparse
import re
from typing import Optional, List, Dict, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

def load_env_file():
    """自動載入同目錄下的 .env 檔案"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, '..', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

load_env_file()  # 程式啟動時自動載入

def require_psycopg2():
    if not HAS_PSYCOPG2:
        print("請先安裝 psycopg2-binary: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

def get_db_connection():
    """建立資料庫連線"""
    require_psycopg2()
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
            SELECT column_name, data_type, is_nullable, column_default, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
    else:
        cur.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return json.dumps(rows, indent=2, default=str)


def get_database_schema() -> Dict[str, Any]:
    """取得完整資料庫 schema"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 取得所有表
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [r[0] for r in cur.fetchall()]
    
    schema = {}
    for table in tables:
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        schema[table] = [dict(r) for r in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return schema


def generate_sql(nl_query: str, table_name: Optional[str] = None, openai_key: Optional[str] = None) -> str:
    """使用 OpenAI 將自然語言轉換為 SQL"""
    api_key = openai_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "-- 錯誤: 請設定 OPENAI_API_KEY 環境變數"
    
    # 取得 schema
    if table_name:
        schema = {table_name: json.loads(get_table_schema(table_name))}
    else:
        schema = get_database_schema()
    
    schema_str = json.dumps(schema, indent=2, default=str)
    
    # 建立 prompt
    prompt = f"""你是一個 PostgreSQL SQL 專家。根據以下資料庫結構，將自然語言轉換為 PostgreSQL SQL 語句。

重要規則：
1. 只輸出 SQL 語句，不要有任何其他解釋或文字
2. 如果是 SELECT 查詢，可加上 LIMIT，除非查詢中明確說明不限筆數
3. 如果是建立表格，需要包含 PRIMARY KEY
4. 字串值使用單引號 ' '
5. 欄位名稱使用雙引號 " " 如果包含特殊字元

資料庫結構:
{schema_str}

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
    
    # 安全檢查 - 禁止危險操作
    dangerous = ['DROP DATABASE', 'TRUNCATE', 'pg_', 'information_schema']
    for d in dangerous:
        if d in sql.upper() and d != 'information_schema':
            return [], sql, f"安全警告: 不允許執行 {d}"
    
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


def format_schema(data: list, title: str = "Schema") -> str:
    """格式化 schema 輸出"""
    lines = [f"=== {title} ==="]
    if isinstance(data, dict):
        for table, columns in data.items():
            lines.append(f"\n[{table}]")
            for col in columns:
                nullable = "NULL" if col.get("is_nullable") == "YES" else "NOT NULL"
                default = f"DEFAULT {col['column_default']}" if col.get("column_default") else ""
                length = f"({col['character_maximum_length']})" if col.get("character_maximum_length") else ""
                lines.append(f"  {col['column_name']:20} {col['data_type']}{length:15} {nullable:8} {default}")
    else:
        for col in data:
            nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col.get("column_default") else ""
            lines.append(f"  {col['column_name']:20} {col['data_type']:20} {nullable}")
    return "\n".join(lines)


def main():
    if not HAS_PSYCOPG2:
        print("請先安裝 psycopg2-binary: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)
    
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
        print(format_schema(json.loads(schema), f"{args.table} 結構"))
        return
    
    # Schema 模式
    if args.schema:
        schema = get_database_schema()
        print(format_schema(schema, "資料庫 Schema"))
        return
    
    # 需要自然語言查詢
    if not args.query:
        parser.print_help()
        print("\n範例:")
        print('  pg_query.py "找出所有年齡大於 30 歲的用戶"')
        print('  pg_query.py "在 users 表新增 name=John, age=25"')
        print('  pg_query.py --describe users')
        print('  pg_query.py --schema')
        return
    
    # 生成 SQL
    sql = generate_sql(args.query, args.table, args.api_key)
    
    print(f"=== 生成的 SQL ===")
    print(sql)
    
    if args.dry_run:
        return
    
    print(f"\n=== 執行結果 ===")
    rows, executed_sql, msg = execute_sql(sql)
    
    if rows:
        print(format_results(rows))
    
    print(f"\n{msg}")


if __name__ == "__main__":
    main()