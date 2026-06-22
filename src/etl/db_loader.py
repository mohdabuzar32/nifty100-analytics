import os
import sqlite3
import pandas as pd
from src.etl.loader import load_all_tables

DB_PATH = "nifty100.db"
SCHEMA_PATH = "db/schema.sql"

TABLE_ORDER = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "documents",
    "prosandcons",
    "analysis",
    "stock_prices",
    "sectors",
    "peer_groups",
    "market_cap",
    "financial_ratios",
]


def create_schema(conn):
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)


def patch_missing_companies(tables):
    known_companies = set(tables["companies"]["id"].dropna())
    missing = set()
    for table_name, df in tables.items():
        if table_name == "companies" or "company_id" not in df.columns:
            continue
        missing |= set(df["company_id"].dropna()) - known_companies

    if missing:
        print(f"Auto-adding {len(missing)} missing companies as placeholders: {sorted(missing)}")
        placeholder_rows = pd.DataFrame({
            "id": sorted(missing),
            "company_logo": None,
            "company_name": sorted(missing),
            "chart_link": None,
            "about_company": None,
            "website": None,
            "nse_profile": None,
            "bse_profile": None,
            "face_value": None,
            "book_value": None,
            "roce_percentage": None,
            "roe_percentage": None,
        })
        tables["companies"] = pd.concat([tables["companies"], placeholder_rows], ignore_index=True)
    return tables


def load_data_into_db(conn, tables):
    for table_name in TABLE_ORDER:
        df = tables[table_name]
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"Inserted {len(df)} rows into {table_name}")


def run_fk_check(conn):
    cursor = conn.execute("PRAGMA foreign_key_check;")
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    create_schema(conn)
    print("Schema created.\n")

    tables = load_all_tables()
    tables = patch_missing_companies(tables)
    print("\nLoading data into SQLite...\n")
    load_data_into_db(conn, tables)
    conn.commit()

    print("\nRunning foreign_key_check...")
    fk_violations = run_fk_check(conn)
    print(f"FK violations found: {len(fk_violations)}")

    count = conn.execute("SELECT COUNT(*) FROM companies;").fetchone()[0]
    print(f"\nSELECT COUNT(*) FROM companies = {count}")

    conn.close()
    print(f"\nDatabase saved at: {DB_PATH}")