import pandas as pd
from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)

pl = pd.read_excel("data/raw/profitandloss.xlsx", sheet_name="Profit & Loss", header=1)
bs = pd.read_excel("data/raw/balancesheet.xlsx", sheet_name="Balance Sheet", header=1)
sectors = pd.read_excel("data/raw/sectors.xlsx")

df = pl.merge(bs, on=["company_id", "year"], suffixes=("_pl", "_bs"))
df = df.merge(sectors[["company_id", "broad_sector"]], on="company_id", how="left")

df["debt_to_equity"] = df.apply(
    lambda r: debt_to_equity(r["borrowings"], r["equity_capital"], r["reserves"]), axis=1
)
df["high_leverage_flag"] = df.apply(
    lambda r: high_leverage_flag(r["debt_to_equity"], r["broad_sector"]), axis=1
)

icr_result = df.apply(
    lambda r: interest_coverage_ratio(r["operating_profit"], r["other_income"], r["interest"]), axis=1
)
df["interest_coverage"] = icr_result.apply(lambda x: x[0])
df["icr_label"] = icr_result.apply(lambda x: x[1])

df["icr_warning_flag"] = df["interest_coverage"].apply(icr_warning_flag)
df["net_debt"] = df.apply(lambda r: net_debt(r["borrowings"], r["investments"]), axis=1)
df["asset_turnover"] = df.apply(
    lambda r: asset_turnover(r["sales"], r["total_assets"]), axis=1
)

print(f"Total rows processed: {len(df)}")
print(df[[
    "company_id", "year", "broad_sector",
    "debt_to_equity", "high_leverage_flag",
    "interest_coverage", "icr_label", "icr_warning_flag",
    "net_debt", "asset_turnover"
]].head(10))

print("\nNull counts:")
print(df[["debt_to_equity", "interest_coverage", "asset_turnover"]].isnull().sum())

print("\nDebt-free companies (icr_label = 'Debt Free'):", (df["icr_label"] == "Debt Free").sum())
print("High leverage flagged rows:", df["high_leverage_flag"].sum())
print("ICR warning flagged rows (at risk):", df["icr_warning_flag"].sum())

df.to_csv("output/day09_leverage_ratios.csv", index=False)
print("\nSaved to output/day09_leverage_ratios.csv")