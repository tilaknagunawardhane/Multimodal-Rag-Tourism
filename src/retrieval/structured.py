# This pipeline handles factual, parametric queries (e.g., entrance fees, district, opening hours) by converting user intents into SQL or executing parameterized queries on Neon PostgreSQL.

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables dynamically
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))
DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def run_structured_query(sql_query: str):
    """
    Executes a raw SQL SELECT query against PostgreSQL and returns results as dictionaries.
    """
    conn = get_db_connection()
    # RealDictCursor returns rows as Python dictionaries: {'name': 'Sigiriya', 'entrance_fee_lkr': 11305, ...}
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def filter_attractions_by_fee(max_fee_lkr: int):
    """
    Convenience function for structured queries filtering by budget.
    """
    query = "SELECT * FROM attractions WHERE entrance_fee_lkr <= %s ORDER BY entrance_fee_lkr ASC;"
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(query, (max_fee_lkr,))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in results]