import sqlite3
import random

DB_PATH = "nifty100.db"


def get_random_companies(conn, n=5):
    rows = conn.execute("SELECT id, company_name FROM companies WHERE company_logo IS NOT NULL ORDER BY RANDOM() LIMIT ?;", (n,)).fetchall()
    return rows


def check_company_detail(conn, company_id):
    print(f"\n{'='*60}")
    print(f"Company: {company_id}")
    print(f"{'='*60}")

    pl_years = conn.execute("SELECT DISTINCT year FROM profitandloss WHERE company_id = ? ORDER BY year;", (company_id,)).fetchall()
    pl_years = [y[0] for y in pl_years]
    print(f"P&L years available ({len(pl_years)}): {pl_years}")

    bs_years = conn.execute("SELECT DISTINCT year FROM balancesheet WHERE company_id = ? ORDER BY year;", (company_id,)).fetchall()
    bs_years = [y[0] for y in bs_years]
    print(f"Balance Sheet years available ({len(bs_years)}): {bs_years}")

    cf_years = conn.execute("SELECT DISTINCT year FROM cashflow WHERE company_id = ? ORDER BY year;", (company_id,)).fetchall()
    cf_years = [y[0] for y in cf_years]
    print(f"Cash Flow years available ({len(cf_years)}): {cf_years}")

    sp_count = conn.execute("SELECT COUNT(*) FROM stock_prices WHERE company_id = ?;", (company_id,)).fetchone()[0]
    print(f"Stock price records: {sp_count}")


def find_companies_with_low_coverage(conn, threshold=5):
    rows = conn.execute("""
        SELECT company_id, COUNT(DISTINCT year) as year_count
        FROM profitandloss
        GROUP BY company_id
        HAVING year_count < ?
        ORDER BY year_count ASC;
    """, (threshold,)).fetchall()
    return rows


def find_placeholder_companies(conn):
    rows = conn.execute("SELECT id, company_name FROM companies WHERE company_logo IS NULL;").fetchall()
    return rows


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)

    print("STEP 1: Checking 5 random companies\n")
    sample = get_random_companies(conn, 5)
    for company_id, company_name in sample:
        check_company_detail(conn, company_id)

    print(f"\n\n{'='*60}")
    print("STEP 2: Companies with less than 5 years of P&L data")
    print(f"{'='*60}")
    low_coverage = find_companies_with_low_coverage(conn, threshold=5)
    if low_coverage:
        for company_id, year_count in low_coverage:
            print(f"  {company_id}: only {year_count} years of data")
    else:
        print("  None found.")

    print(f"\n\n{'='*60}")
    print("STEP 3: Placeholder companies (missing real company details)")
    print(f"{'='*60}")
    placeholders = find_placeholder_companies(conn)
    if placeholders:
        for company_id, company_name in placeholders:
            print(f"  {company_id}: {company_name}")
    else:
        print("  None found.")

    conn.close()