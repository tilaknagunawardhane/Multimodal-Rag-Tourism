# Handles factual queries on Neon PostgreSQL using dynamic, parameterized SQL building.
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))

DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def run_structured_query(sql_query: str, params: tuple = ()):
    """
    Executes a parameterized SQL SELECT query against PostgreSQL and returns dictionary rows.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute(sql_query, params)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"  SQL Execution Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def search_structured_attractions(category: str = None, district: str = None, max_budget_lkr: int = None):
    """
    Dynamically builds and executes a parameterized SQL query based ONLY on provided parameters.
    No default values are injected if parameters are None.
    """
    sql = "SELECT attraction_id, name, category, district, entrance_fee_lkr, opening_hours, best_season_to_visit FROM attractions"
    conditions = []
    params = []

    if category:
        conditions.append("category ILIKE %s")
        params.append(f"%{category}%")

    if district:
        conditions.append("district ILIKE %s")
        params.append(f"%{district}%")

    if max_budget_lkr is not None:
        conditions.append("entrance_fee_lkr <= %s")
        params.append(max_budget_lkr)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY entrance_fee_lkr ASC;"

    return run_structured_query(sql, tuple(params))