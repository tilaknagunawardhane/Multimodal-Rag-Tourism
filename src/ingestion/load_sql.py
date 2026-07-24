import psycopg2
import csv
import os
from dotenv import load_dotenv

# Load connection string from .env
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# Dynamically construct the path relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, "../../data/tourism_data.csv")

def load_relational_data():
    print("Connecting to Neon PostgreSQL...")
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    # 1. Create the table schema
    print("Creating table schema...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attractions (
            attraction_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(255),
            category VARCHAR(100),
            district VARCHAR(100),
            entrance_fee_lkr INT,
            opening_hours VARCHAR(50),
            best_season_to_visit VARCHAR(50)
        );
    """)

    # Clear existing data in case you run this script multiple times
    cursor.execute("TRUNCATE TABLE attractions;")

    # 2. Insert data from CSV
    print(f"Reading data from {CSV_PATH}...")
    with open(CSV_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute("""
                INSERT INTO attractions (attraction_id, name, category, district, entrance_fee_lkr, opening_hours, best_season_to_visit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row['attraction_id'], row['name'], row['category'], row['district'],
                int(row['entrance_fee_lkr']), row['opening_hours'], row['best_season_to_visit']
            ))
            print(f"Inserted: {row['name']}")

    # 3. Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Relational data successfully loaded into Neon PostgreSQL!")

if __name__ == "__main__":
    load_relational_data()