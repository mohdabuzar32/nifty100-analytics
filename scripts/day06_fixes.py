import sqlite3

DB_PATH = "nifty100.db"

REAL_DETAILS = {
    "AGTL": {"company_name": "Adani Green Energy Ltd", "website": "https://www.adanigreenenergy.com"},
    "ULTRACEMCO": {"company_name": "UltraTech Cement Ltd", "website": "https://www.ultratechcement.com"},
    "UNIONBANK": {"company_name": "Union Bank of India", "website": "https://www.unionbankofindia.co.in"},
    "UNITDSPR": {"company_name": "United Spirits Ltd", "website": "https://www.unitedspirits.in"},
    "VBL": {"company_name": "Varun Beverages Ltd", "website": "https://www.varunbeverages.com"},
    "VEDL": {"company_name": "Vedanta Ltd", "website": "https://www.vedantalimited.com"},
    "WIPRO": {"company_name": "Wipro Ltd", "website": "https://www.wipro.com"},
    "ZOMATO": {"company_name": "Eternal Ltd (Zomato)", "website": "https://www.eternal.in"},
    "ZYDUSLIFE": {"company_name": "Zydus Lifesciences Ltd", "website": "https://www.zyduslife.com"},
    "LTIM": {"company_name": "LTIMindtree Ltd", "website": "https://www.ltimindtree.com"},
}


def fix_1_update_placeholder_companies(conn):
    print("FIX 1: Updating placeholder companies with real names/websites")
    print("-" * 60)
    for ticker, details in REAL_DETAILS.items():
        conn.execute(
            "UPDATE companies SET company_name = ?, website = ? WHERE id = ?;",
            (details["company_name"], details["website"], ticker)
        )
        print(f"  {ticker} -> {details['company_name']}")
    conn.commit()
    print()


def fix_2_remove_cashflow_duplicates(conn):
    print("FIX 2: Removing duplicate (company_id, year) rows in cashflow")
    print("-" * 60)
    before = conn.execute("SELECT COUNT(*) FROM cashflow;").fetchone()[0]

    conn.execute("""
        DELETE FROM cashflow
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM cashflow
            GROUP BY company_id, year
        );
    """)
    conn.commit()

    after = conn.execute("SELECT COUNT(*) FROM cashflow;").fetchone()[0]
    print(f"  Rows before: {before}")
    print(f"  Rows after:  {after}")
    print(f"  Removed:     {before - after} duplicate rows")
    print()


def fix_3_remove_financial_ratios_duplicates(conn):
    print("FIX 3: Removing duplicate (company_id, year) rows in financial_ratios")
    print("-" * 60)
    before = conn.execute("SELECT COUNT(*) FROM financial_ratios;").fetchone()[0]

    conn.execute("""
        DELETE FROM financial_ratios
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM financial_ratios
            GROUP BY company_id, year
        );
    """)
    conn.commit()

    after = conn.execute("SELECT COUNT(*) FROM financial_ratios;").fetchone()[0]
    print(f"  Rows before: {before}")
    print(f"  Rows after:  {after}")
    print(f"  Removed:     {before - after} duplicate rows")
    print()


def fix_4_flag_low_coverage(conn):
    print("FIX 4 (FLAG ONLY - genuine data gaps, not bugs):")
    print("-" * 60)
    low_coverage = conn.execute("""
        SELECT company_id, COUNT(DISTINCT year) as year_count
        FROM profitandloss
        GROUP BY company_id
        HAVING year_count < 5
        ORDER BY year_count ASC;
    """).fetchall()
    for company_id, count in low_coverage:
        print(f"  {company_id}: only {count} years (likely recent IPO/listing)")

    cf_zero = conn.execute("""
        SELECT c.id FROM companies c
        WHERE c.id NOT IN (SELECT DISTINCT company_id FROM cashflow)
    """).fetchall()
    if cf_zero:
        print(f"\n  Companies with 0 cashflow records: {[r[0] for r in cf_zero]} (genuine data gap)")
    print()


def fix_5_verify_no_duplicates_remain(conn):
    print("VERIFICATION: Checking no duplicates remain")
    print("-" * 60)
    cf_dups = conn.execute("""
        SELECT company_id, year, COUNT(*) c FROM cashflow
        GROUP BY company_id, year HAVING c > 1
    """).fetchall()
    fr_dups = conn.execute("""
        SELECT company_id, year, COUNT(*) c FROM financial_ratios
        GROUP BY company_id, year HAVING c > 1
    """).fetchall()
    print(f"  Remaining cashflow duplicates: {len(cf_dups)}")
    print(f"  Remaining financial_ratios duplicates: {len(fr_dups)}")

    fk_violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    print(f"  FK violations: {len(fk_violations)}")
    print()


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    fix_1_update_placeholder_companies(conn)
    fix_2_remove_cashflow_duplicates(conn)
    fix_3_remove_financial_ratios_duplicates(conn)
    fix_4_flag_low_coverage(conn)
    fix_5_verify_no_duplicates_remain(conn)

    print("All Day 06 fixes applied successfully.")
    conn.close()