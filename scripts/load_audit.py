import os
import sqlite3
import csv

DB_PATH = "nifty100.db"
OUTPUT_PATH = "output/load_audit.csv"

EXPECTED_COUNTS = {
    "companies": 92,
    "profitandloss": 1276,
    "balancesheet": 1312,
    "cashflow": 1187,
    "stock_prices": 5520,
}

TABLES = [
    "companies", "profitandloss", "balancesheet", "cashflow", "documents",
    "prosandcons", "analysis", "stock_prices", "sectors", "peer_groups",
    "market_cap", "financial_ratios"
]


def run_audit():
    conn = sqlite3.connect(DB_PATH)
    rows = []

    for table in TABLES:
        actual_count = conn.execute(f"SELECT COUNT(*) FROM {table};").fetchone()[0]
        expected = EXPECTED_COUNTS.get(table, actual_count)
        rejected = max(0, expected - actual_count) if table in EXPECTED_COUNTS else 0
        extra = max(0, actual_count - expected) if table in EXPECTED_COUNTS else 0

        if table in EXPECTED_COUNTS:
            status = "OK" if actual_count >= expected else "MISMATCH"
        else:
            status = "OK"

        rows.append({
            "table_name": table,
            "rows_loaded": actual_count,
            "expected_rows": expected if table in EXPECTED_COUNTS else "N/A",
            "rejected_rows": rejected,
            "extra_rows": extra,
            "status": status
        })

    fk_violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
    conn.close()

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["table_name", "rows_loaded", "expected_rows", "rejected_rows", "extra_rows", "status"])
        writer.writeheader()
        writer.writerows(rows)

    print("Load Audit Summary")
    print("-" * 70)
    for r in rows:
        print(f"{r['table_name']:<20} loaded={r['rows_loaded']:<6} expected={r['expected_rows']:<6} status={r['status']}")
    print("-" * 70)
    print(f"FK violations: {len(fk_violations)}")
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    run_audit()