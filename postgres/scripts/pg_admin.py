#!/usr/bin/env python3
"""
PostgreSQL 管理與監控工具
參考 mukul975/postgres-mcp-server 設計
支援：資料庫管理、效能監控、索引維護、連線管理等
"""

import os
import sys
import json
import argparse
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


def get_db_connection(database: str = None):
    """建立資料庫連線"""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        database=database or os.getenv("PG_DATABASE", "postgres"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", ""),
        cursor_factory=RealDictCursor
    )


def format_table(rows: List[Dict], headers: Optional[List[str]] = None) -> str:
    """格式化表格輸出"""
    if not rows:
        return "(無資料)"
    
    if headers:
        h = headers
    else:
        h = list(rows[0].keys())
    
    col_widths = {k: max(len(str(k)), max(len(str(r.get(k, ""))) for r in rows)) for k in h}
    
    header_line = " | ".join(k.ljust(col_widths[k]) for k in h)
    separator = "-+-".join("-" * col_widths[k] for k in h)
    
    data_lines = []
    for row in rows:
        line = " | ".join(str(row.get(k, "")).ljust(col_widths[k]) for k in h)
        data_lines.append(line)
    
    return "\n".join([header_line, separator] + data_lines)


# ========== 資料庫操作 ==========

def list_databases() -> str:
    """列出所有資料庫"""
    conn = get_db_connection("postgres")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT datname as name, 
               pg_database_size(datname) as size_bytes,
               rolname as owner
        FROM pg_database d
        JOIN pg_authid a ON d.datdba = a.oid
        WHERE datistemplate = false
        ORDER BY datname
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    result = ["=== 資料庫列表 ==="]
    result.append(format_table(rows))
    result.append("")
    
    # 格式化大小
    for row in rows:
        size_mb = row['size_bytes'] / (1024 * 1024)
        result.append(f"  {row['name']}: {size_mb:.2f} MB")
    
    return "\n".join(result)


def list_tables(schema: str = "public") -> str:
    """列出所有資料表"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT t.table_name, 
               pg_table_size(c.oid) as size_bytes,
               (SELECT reltuples::bigint FROM pg_class WHERE oid = c.oid) as row_count
        FROM information_schema.tables t
        JOIN pg_class c ON c.relname = t.table_name
        WHERE t.table_schema = %s AND t.table_type = 'BASE TABLE'
        ORDER BY t.table_name
    """, (schema,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    result = [f"=== {schema} 資料表 ==="]
    result.append(format_table(rows))
    
    return "\n".join(result)


def list_indexes(table: Optional[str] = None, schema: str = "public") -> str:
    """列出索引"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if table:
        cur.execute("""
            SELECT indexname, tablename, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s
            ORDER BY indexname
        """, (schema, table))
    else:
        cur.execute("""
            SELECT indexname, tablename, indexdef
            FROM pg_indexes
            WHERE schemaname = %s
            ORDER BY tablename, indexname
        """, (schema,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    title = f"{table} 表的索引" if table else "=== 所有索引 ==="
    return format_table(rows, ["indexname", "tablename", "indexdef"])


def describe_table(table_name: str, schema: str = "public") -> str:
    """取得資料表詳細結構"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, table_name))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    result = [f"=== {table_name} 結構 ==="]
    result.append(format_table(rows, ["column_name", "data_type", "is_nullable", "column_default"]))
    
    return "\n".join(result)


# ========== 效能監控 ==========

def get_slow_queries(limit: int = 10) -> str:
    """取得慢查詢"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            pid,
            now() - pg_stat_activity.query_start AS duration,
            usename AS username,
            datname AS database,
            state,
            left(query, 200) AS query
        FROM pg_stat_activity
        WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds'
          AND state = 'active'
          AND query NOT LIKE '%pg_stat_activity%'
        ORDER BY duration DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return f"=== 慢查詢 (>{limit}) ===\n" + format_table(rows)


def get_active_connections() -> str:
    """取得活躍連線"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            pid,
            usename AS username,
            datname AS database,
            state,
            now() - pg_stat_activity.query_start AS duration,
            left(query, 100) AS query
        FROM pg_stat_activity
        WHERE state != 'idle'
        ORDER BY duration DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 活躍連線 ===\n" + format_table(rows)


def get_connection_stats() -> str:
    """取得連線統計"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            state,
            COUNT(*) as count
        FROM pg_stat_activity
        GROUP BY state
        ORDER BY count DESC
    """)
    state_rows = cur.fetchall()
    
    cur.execute("SELECT setting::int as value FROM pg_settings WHERE name = 'max_connections'")
    max_conn = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) as current FROM pg_stat_activity")
    current_conn = cur.fetchone()
    
    cur.close()
    conn.close()
    
    result = ["=== 連線統計 ==="]
    result.append(format_table(state_rows))
    result.append(f"\n最大連線數: {max_conn['value']}")
    result.append(f"目前連線: {current_conn['current']}")
    
    return "\n".join(result)


def get_db_size() -> str:
    """取得資料庫大小"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            datname as database,
            pg_database_size(datname) as size_bytes
        FROM pg_database
        WHERE datistemplate = false
        ORDER BY pg_database_size(datname) DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    result = ["=== 資料庫大小 ==="]
    for row in rows:
        size_mb = row['size_bytes'] / (1024 * 1024)
        result.append(f"  {row['database']}: {size_mb:.2f} MB")
    
    return "\n".join(result)


def get_table_size(table_name: str) -> str:
    """取得資料表大小"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            t.table_name,
            pg_table_size(c.oid) as table_size,
            pg_indexes_size(c.oid) as indexes_size,
            pg_total_relation_size(c.oid) as total_size,
            pg_num_live_tup(c.oid) as live_rows,
            pg_num_dead_tup(c.oid) as dead_rows
        FROM information_schema.tables t
        JOIN pg_class c ON c.relname = t.table_name
        WHERE t.table_schema = 'public' AND t.table_name = %s
    """, (table_name,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if not row:
        return f"資料表 {table_name} 不存在"
    
    result = [f"=== {table_name} 大小 ==="]
    result.append(f"  資料表大小: {row['table_size'] / 1024:.2f} KB")
    result.append(f"  索引大小: {row['indexes_size'] / 1024:.2f} KB")
    result.append(f"  總大小: {row['total_size'] / 1024:.2f} KB")
    result.append(f"  活躍列數: {row['live_rows']}")
    result.append(f"  死亡列數: {row['dead_rows']}")
    
    return "\n".join(result)


def get_top_tables(limit: int = 10) -> str:
    """取得最大的 N 個表"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            t.table_name,
            pg_total_relation_size(c.oid) as size_bytes,
            pg_num_live_tup(c.oid) as row_count
        FROM information_schema.tables t
        JOIN pg_class c ON c.relname = t.table_name
        WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'
        ORDER BY pg_total_relation_size(c.oid) DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    result = [f"=== 前 {limit} 大資料表 ==="]
    for row in rows:
        size_mb = row['size_bytes'] / (1024 * 1024)
        result.append(f"  {row['table_name']:30} {size_mb:8.2f} MB ({row['row_count']:,} 列)")
    
    return "\n".join(result)


def get_cache_hit_ratio() -> str:
    """取得快取命中率"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            round(100 * sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)), 2) as hit_ratio
        FROM pg_stat_bgwriter
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    ratio = row['hit_ratio'] if row else 0
    status = "良好" if ratio > 95 else "一般" if ratio > 90 else "需優化"
    
    return f"=== 快取命中率 ===\n  {ratio}% ({status})"


def get_long_transactions() -> str:
    """取得長事務"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            pid,
            usename AS username,
            datname AS database,
            now() - xact_start AS duration,
            state,
            left(query, 100) AS query
        FROM pg_stat_activity
        WHERE xact_start IS NOT NULL
          AND state != 'idle'
          AND (now() - xact_start) > interval '1 minute'
        ORDER BY xact_start
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 長事務 (>1 分鐘) ===\n" + format_table(rows)


# ========== 鎖管理 ==========

def get_locks() -> str:
    """取得目前鎖"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            l.pid,
            l.locktype,
            l.mode,
            l.relation::regclass as table,
            l.granted,
            a.usename AS username,
            left(a.query, 100) AS query
        FROM pg_locks l
        JOIN pg_stat_activity a ON l.pid = a.pid
        WHERE l.relation IS NOT NULL
        ORDER BY l.granted, l.pid
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 目前鎖 ===\n" + format_table(rows)


def get_blocking_queries() -> str:
    """取得阻塞查詢"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            blocked.pid AS blocked_pid,
            blocked.usename AS blocked_user,
            blocked.query AS blocked_query,
            blocking.pid AS blocking_pid,
            blocking.usename AS blocking_user,
            blocking.query AS blocking_query
        FROM pg_stat_activity blocked
        JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
        WHERE blocked.pid != pg_backend_pid()
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 阻塞查詢 ===\n" + format_table(rows)


# ========== 索引管理 ==========

def get_unused_indexes() -> str:
    """取得未使用的索引"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            schemaname,
            tablename,
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
            idx_scan as scans
        FROM pg_stat_user_indexes
        WHERE idx_scan = 0
          AND indexrelid NOT IN (
              SELECT conindid FROM pg_constraint WHERE contype IN ('p', 'u')
          )
        ORDER BY pg_relation_size(indexrelid) DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 未使用的索引 ===\n" + format_table(rows)


def create_index(index_name: str, table_name: str, column: str, unique: bool = False) -> str:
    """建立索引"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    unique_str = "UNIQUE " if unique else ""
    sql = f'CREATE {unique_str}INDEX CONCURRENTLY IF NOT EXISTS "{index_name}" ON "{table_name}" ("{column}")'
    
    try:
        cur.execute(sql)
        conn.commit()
        return f"✓ 索引 {index_name} 已建立在 {table_name}({column}) 上"
    except Exception as e:
        conn.rollback()
        return f"✗ 建立索引失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


def drop_index(index_name: str) -> str:
    """刪除索引"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    sql = f'DROP INDEX IF EXISTS "{index_name}"'
    
    try:
        cur.execute(sql)
        conn.commit()
        return f"✓ 索引 {index_name} 已刪除"
    except Exception as e:
        conn.rollback()
        return f"✗ 刪除索引失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


# ========== 維護操作 ==========

def vacuum(table_name: Optional[str] = None) -> str:
    """執行 VACUUM"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if table_name:
        sql = f'VACUUM ANALYZE "{table_name}"'
    else:
        sql = 'VACUUM ANALYZE'
    
    try:
        cur.execute(sql)
        conn.commit()
        return f"✓ VACUUM {'對 ' + table_name + ' ' if table_name else ''}執行完成"
    except Exception as e:
        conn.rollback()
        return f"✗ VACUUM 失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


def analyze(table_name: Optional[str] = None) -> str:
    """執行 ANALYZE"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if table_name:
        sql = f'ANALYZE "{table_name}"'
    else:
        sql = 'ANALYZE'
    
    try:
        cur.execute(sql)
        conn.commit()
        return f"✓ ANALYZE {'對 ' + table_name + ' ' if table_name else ''}執行完成"
    except Exception as e:
        conn.rollback()
        return f"✗ ANALYZE 失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


def reindex(table_name: Optional[str] = None) -> str:
    """執行 REINDEX"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    if table_name:
        sql = f'REINDEX TABLE "{table_name}"'
    else:
        sql = 'REINDEX DATABASE ' + os.getenv("PG_DATABASE", "postgres")
    
    try:
        cur.execute(sql)
        conn.commit()
        return f"✓ REINDEX {'對 ' + table_name + ' ' if table_name else ''}執行完成"
    except Exception as e:
        conn.rollback()
        return f"✗ REINDEX 失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


# ========== 查詢分析 ==========

def explain_query(query: str) -> str:
    """分析查詢執行計劃"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(f"EXPLAIN (FORMAT JSON) {query}")
        plan = cur.fetchone()
        return f"=== 執行計劃 ===\n" + json.dumps(plan[0], indent=2)
    except Exception as e:
        return f"✗ 分析失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


def explain_analyze(query: str) -> str:
    """分析查詢執行計劃（實際執行）"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
        plan = cur.fetchone()
        return f"=== 執行計劃 ===\n" + json.dumps(plan[0], indent=2)
    except Exception as e:
        return f"✗ 分析失敗: {str(e)}"
    finally:
        cur.close()
        conn.close()


# ========== 用戶管理 ==========

def list_roles() -> str:
    """列出所有角色"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            rolname AS role_name,
            rolsuper AS is_superuser,
            rolinherit AS is_inherit,
            rolcreaterole AS can_create_role,
            rolcreatedb AS can_create_db,
            rolcanlogin AS can_login,
            rolreplication AS is_replication,
            rolvaliduntil AS valid_until
        FROM pg_roles
        ORDER BY rolname
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 角色列表 ===\n" + format_table(rows)


def list_users() -> str:
    """列出可登入用戶"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            rolname AS username,
            rolvaliduntil AS valid_until
        FROM pg_roles
        WHERE rolcanlogin = true
        ORDER BY rolname
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return "=== 可登入用戶 ===\n" + format_table(rows)


# ========== 複製狀態 ==========

def get_replication_status() -> str:
    """取得複製狀態"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            pid,
            state,
            usesysid AS user_id,
            application_name,
            client_addr,
            backend_start,
            backend_xmin
        FROM pg_stat_replication
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    if not rows:
        return "=== 複製狀態 ===\n  (無複製連線)"
    
    return "=== 複製狀態 ===\n" + format_table(rows)


# ========== 健康檢查 ==========

def health_check() -> str:
    """健康檢查"""
    results = []
    status = "✓"
    
    # 連線測試
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        cur.close()
        conn.close()
        results.append(f"✓ 資料庫連線正常")
        results.append(f"  版本: {version['version'][:50]}...")
    except Exception as e:
        results.append(f"✗ 資料庫連線失敗: {str(e)}")
        status = "✗"
    
    # 連線數
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as count FROM pg_stat_activity")
        count = cur.fetchone()
        cur.execute("SELECT setting::int FROM pg_settings WHERE name = 'max_connections'")
        max_conn = cur.fetchone()
        cur.close()
        conn.close()
        
        usage = count['count'] / max_conn['setting'] * 100
        results.append(f"  連線數: {count['count']}/{max_conn['setting']} ({usage:.1f}%)")
        if usage > 80:
            results.append(f"⚠ 連線數接近上限")
            status = "⚠"
    except Exception as e:
        results.append(f"✗ 無法取得連線資訊: {str(e)}")
    
    # 快取命中率
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT round(100 * sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)), 2) as ratio
            FROM pg_stat_bgwriter
        """)
        ratio = cur.fetchone()
        cur.close()
        conn.close()
        results.append(f"  快取命中率: {ratio['ratio']}%")
        if ratio['ratio'] < 90:
            results.append(f"⚠ 快取命中率過低，建議調優")
            status = "⚠"
    except:
        pass
    
    # 死亡列
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT sum(pg_num_dead_tup) as dead_rows FROM pg_stat_user_tables")
        dead = cur.fetchone()
        cur.close()
        conn.close()
        results.append(f"  死亡列數: {dead['dead_rows']}")
        if dead['dead_rows'] > 10000:
            results.append(f"⚠ 死亡列過多，建議執行 VACUUM")
            status = "⚠"
    except:
        pass
    
    results.insert(0, f"=== 健康檢查 [{status}] ===")
    
    return "\n".join(results)


# ========== 主程式 ==========

def main():
    if not HAS_PSYCOPG2:
        print("請先安裝 psycopg2-binary: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="PostgreSQL 管理與監控工具")
    
    # 列表操作
    group_list = parser.add_argument_group("列表操作")
    group_list.add_argument("--list-databases", action="store_true", help="列出所有資料庫")
    group_list.add_argument("--list-tables", action="store_true", help="列出所有資料表")
    group_list.add_argument("--list-indexes", "-i", metavar="TABLE", help="列出索引（可指定表名）")
    group_list.add_argument("--list-roles", action="store_true", help="列出所有角色")
    group_list.add_argument("--list-users", action="store_true", help="列出可登入用戶")
    
    # 查詢操作
    group_query = parser.add_argument_group("查詢操作")
    group_query.add_argument("--describe", "-d", metavar="TABLE", help="顯示資料表結構")
    group_query.add_argument("--explain", "-e", metavar="SQL", help="分析查詢執行計劃")
    group_query.add_argument("--explain-analyze", metavar="SQL", help="分析查詢（實際執行）")
    
    # 效能監控
    group_perf = parser.add_argument_group("效能監控")
    group_perf.add_argument("--slow-queries", action="store_true", help="顯示慢查詢")
    group_perf.add_argument("--active-connections", action="store_true", help="顯示活躍連線")
    group_perf.add_argument("--connection-stats", action="store_true", help="顯示連線統計")
    group_perf.add_argument("--db-size", action="store_true", help="顯示資料庫大小")
    group_perf.add_argument("--table-size", "-t", metavar="TABLE", help="顯示資料表大小")
    group_perf.add_argument("--top-tables", type=int, metavar="N", help="顯示最大的 N 個表")
    group_perf.add_argument("--cache-hit", action="store_true", help="顯示快取命中率")
    group_perf.add_argument("--long-transactions", action="store_true", help="顯示長事務")
    
    # 鎖管理
    group_lock = parser.add_argument_group("鎖管理")
    group_lock.add_argument("--locks", action="store_true", help="顯示目前鎖")
    group_lock.add_argument("--blocking", action="store_true", help="顯示阻塞查詢")
    
    # 索引管理
    group_index = parser.add_argument_group("索引管理")
    group_index.add_argument("--unused-indexes", action="store_true", help="顯示未使用索引")
    group_index.add_argument("--create-index", nargs=3, metavar=("NAME", "TABLE", "COLUMN"), help="建立索引")
    group_index.add_argument("--drop-index", metavar="NAME", help="刪除索引")
    
    # 維護操作
    group_maint = parser.add_argument_group("維護操作")
    group_maint.add_argument("--vacuum", nargs="?", const="", metavar="TABLE", help="執行 VACUUM ANALYZE")
    group_maint.add_argument("--analyze", nargs="?", const="", metavar="TABLE", help="執行 ANALYZE")
    group_maint.add_argument("--reindex", nargs="?", const="", metavar="TABLE", help="執行 REINDEX")
    
    # 複製
    group_repl = parser.add_argument_group("複製")
    group_repl.add_argument("--replication", action="store_true", help="顯示複製狀態")
    
    # 健康檢查
    group_health = parser.add_argument_group("健康檢查")
    group_health.add_argument("--health-check", action="store_true", help="執行健康檢查")
    
    args = parser.parse_args()
    
    # 執行對應操作
    if args.list_databases:
        print(list_databases())
    elif args.list_tables:
        print(list_tables())
    elif args.list_indexes is not None:
        print(list_indexes(args.list_indexes))
    elif args.list_roles:
        print(list_roles())
    elif args.list_users:
        print(list_users())
    elif args.describe:
        print(describe_table(args.describe))
    elif args.explain:
        print(explain_query(args.explain))
    elif args.explain_analyze:
        print(explain_analyze(args.explain_analyze))
    elif args.slow_queries:
        print(get_slow_queries())
    elif args.active_connections:
        print(get_active_connections())
    elif args.connection_stats:
        print(get_connection_stats())
    elif args.db_size:
        print(get_db_size())
    elif args.table_size:
        print(get_table_size(args.table_size))
    elif args.top_tables:
        print(get_top_tables(args.top_tables))
    elif args.cache_hit:
        print(get_cache_hit_ratio())
    elif args.long_transactions:
        print(get_long_transactions())
    elif args.locks:
        print(get_locks())
    elif args.blocking:
        print(get_blocking_queries())
    elif args.unused_indexes:
        print(get_unused_indexes())
    elif args.create_index:
        name, table, column = args.create_index
        print(create_index(name, table, column))
    elif args.drop_index:
        print(drop_index(args.drop_index))
    elif args.vacuum is not None:
        print(vacuum(args.vacuum or None))
    elif args.analyze is not None:
        print(analyze(args.analyze or None))
    elif args.reindex is not None:
        print(reindex(args.reindex or None))
    elif args.replication:
        print(get_replication_status())
    elif args.health_check:
        print(health_check())
    else:
        parser.print_help()
        print("\n範例:")
        print("  pg_admin.py --health-check")
        print("  pg_admin.py --list-tables")
        print("  pg_admin.py --slow-queries")
        print("  pg_admin.py --db-size")
        print("  pg_admin.py --top-tables 10")
        print("  pg_admin.py --describe users")
        print("  pg_admin.py --explain 'SELECT * FROM users WHERE age > 30'")


if __name__ == "__main__":
    main()