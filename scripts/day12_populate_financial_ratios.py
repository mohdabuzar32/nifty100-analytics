import sqlite3
import pandas as pd
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)
from src.analytics.cashflow_kpis import normalize_year, free_cash_flow

pl = pd.read_excel("data/raw/profitandloss.xlsx", sheet_name="Profit & Loss", header=1)
bs = pd.read_excel("data/raw/balancesheet.xlsx", sheet_name="Balance Sheet", header=1)
cf = pd.read_excel("data/raw/cashflow.xlsx", sheet_name="Cash Flow", header=1)

pl_dupes = pl[pl.duplicated(subset=["company_id", "year"], keep=False)]
bs_dupes = bs[bs.duplicated(subset=["company_id", "year"], keep=False)]
pl_dupes.to_csv("output/day12_pl_duplicates.log", index=False)
bs_dupes.to_csv("output/day12_bs_duplicates.log", index=False)
print(f"Logged {len(pl_dupes)} P&L duplicate rows, {len(bs_dupes)} BS duplicate rows")

pl = pl.sort_values(["company_id", "year"]).drop_duplicates(subset=["company_id", "year"], keep="last")
bs = bs.sort_values(["company_id", "year"]).drop_duplicates(subset=["company_id", "year"], keep="last")

cf["year_norm"] = cf["year"].apply(normalize_year)
cf = cf[cf["year_norm"].notna()].copy()
cf = cf.rename(columns={"year": "year_raw", "year_norm": "year"})
cf = cf.drop_duplicates(subset=["company_id", "year"], keep="last")

pl = pl[pl["year"] != "TTM"].copy()
pl["year_int"] = pl["year"].str.extract(r"(\d{4})")[0].astype(int)
bs["year_int"] = bs["year"].str.extract(r"(\d{4})")[0].astype(int)
cf["year_int"] = cf["year"].str.extract(r"(\d{4})")[0].astype(int)

pl = pl.rename(columns={"year": "year_str"})
bs = bs.rename(columns={"year": "year_str"})
cf = cf.rename(columns={"year": "year_str"})

df = pl.merge(bs, on=["company_id", "year_str"], suffixes=("_pl", "_bs"), how="left")
df = df.merge(cf, on=["company_id", "year_str"], suffixes=("", "_cf"), how="left")

print(f"Merged rows: {len(df)}")

df["net_profit_margin_pct"] = df.apply(
    lambda r: net_profit_margin(r["net_profit"], r["sales"]), axis=1
)

opm_result = df.apply(
    lambda r: operating_profit_margin(r["operating_profit"], r["sales"], r["opm_percentage"]), axis=1
)
df["operating_profit_margin_pct"] = opm_result.apply(lambda x: x[0])

df["return_on_equity_pct"] = df.apply(
    lambda r: return_on_equity(r["net_profit"], r["equity_capital"], r["reserves"]), axis=1
)

df["debt_to_equity"] = df.apply(
    lambda r: debt_to_equity(r["borrowings"], r["equity_capital"], r["reserves"]), axis=1
)

icr_result = df.apply(
    lambda r: interest_coverage_ratio(r["operating_profit"], r["other_income"], r["interest"]), axis=1
)
df["interest_coverage"] = icr_result.apply(lambda x: x[0])

df["asset_turnover"] = df.apply(
    lambda r: asset_turnover(r["sales"], r["total_assets"]), axis=1
)

df["free_cash_flow_cr"] = df.apply(
    lambda r: free_cash_flow(r["operating_activity"], r["investing_activity"])
    if pd.notna(r.get("operating_activity")) else None,
    axis=1
)

df["capex_cr"] = df["investing_activity"].apply(lambda x: abs(x) if pd.notna(x) else None)

df["earnings_per_share"] = df["eps"]

df["book_value_per_share"] = df.apply(
    lambda r: round((r["equity_capital"] + r["reserves"]) / (r["equity_capital"] / 10), 2)
    if r["equity_capital"] > 0 else None,
    axis=1
)

df["dividend_payout_ratio_pct"] = df["dividend_payout"]
df["total_debt_cr"] = df["borrowings"]
df["cash_from_operations_cr"] = df["operating_activity"]

df["year_int"] = df["year_int_pl"]

final_cols = [
    "company_id", "year_int",
    "net_profit_margin_pct", "operating_profit_margin_pct", "return_on_equity_pct",
    "debt_to_equity", "interest_coverage", "asset_turnover",
    "free_cash_flow_cr", "capex_cr", "earnings_per_share", "book_value_per_share",
    "dividend_payout_ratio_pct", "total_debt_cr", "cash_from_operations_cr"
]

final_df = df[final_cols].rename(columns={"year_int": "year"})
final_df["year"] = final_df["year"].astype(int)

npm_outlier = final_df["net_profit_margin_pct"].apply(
    lambda x: pd.notna(x) and (x > 100 or x < -100)
)
roe_outlier = final_df["return_on_equity_pct"].apply(
    lambda x: pd.notna(x) and (x > 100 or x < -100)
)
outliers = final_df[npm_outlier | roe_outlier]
outliers.to_csv("output/day12_ratio_outliers.log", index=False)
print(f"\nOutlier rows flagged: {len(outliers)}")
print(outliers[["company_id", "year", "net_profit_margin_pct", "return_on_equity_pct"]])

print(f"\nFinal row count: {len(final_df)}")
print(final_df.head(5))
print("\nNull counts:")
print(final_df.isnull().sum())

dup_check = final_df[final_df.duplicated(subset=["company_id", "year"], keep=False)]
print(f"\nDuplicate company-year rows in final table: {len(dup_check)}")

conn = sqlite3.connect("nifty100.db")
final_df.to_sql("financial_ratios", conn, if_exists="replace", index_label="id")
conn.commit()

count = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
print(f"\nRows in financial_ratios table: {count}")

conn.close()
print("Done.")