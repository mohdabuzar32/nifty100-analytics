import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")
df = pd.read_sql(
    "SELECT * FROM financial_ratios WHERE company_id IN ('TCS', 'ABB', 'AMBUJACEM') ORDER BY company_id, year",
    conn
)
print(df[["company_id", "year", "net_profit_margin_pct", "return_on_equity_pct", "debt_to_equity"]])
conn.close()