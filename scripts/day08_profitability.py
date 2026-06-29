import pandas as pd
from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    roce_rating,
)

pl = pd.read_excel("data/raw/profitandloss.xlsx", sheet_name="Profit & Loss", header=1)
bs = pd.read_excel("data/raw/balancesheet.xlsx", sheet_name="Balance Sheet", header=1)
sectors = pd.read_excel("data/raw/sectors.xlsx")

df = pl.merge(bs, on=["company_id", "year"], suffixes=("_pl", "_bs"))
df = df.merge(sectors[["company_id", "broad_sector"]], on="company_id", how="left")

df["ebit"] = df["operating_profit"] + df["other_income"]

df["net_profit_margin_pct"] = df.apply(
    lambda r: net_profit_margin(r["net_profit"], r["sales"]), axis=1
)

opm_result = df.apply(
    lambda r: operating_profit_margin(r["operating_profit"], r["sales"], r["opm_percentage"]), axis=1
)
df["operating_profit_margin_pct"] = opm_result.apply(lambda x: x[0])
df["opm_mismatch_flag"] = opm_result.apply(lambda x: x[1])

df["return_on_equity_pct"] = df.apply(
    lambda r: return_on_equity(r["net_profit"], r["equity_capital"], r["reserves"]), axis=1
)
df["return_on_capital_employed_pct"] = df.apply(
    lambda r: return_on_capital_employed(r["ebit"], r["equity_capital"], r["reserves"], r["borrowings"]), axis=1
)
df["return_on_assets_pct"] = df.apply(
    lambda r: return_on_assets(r["net_profit"], r["total_assets"]), axis=1
)

sector_medians = df.groupby("broad_sector")["return_on_capital_employed_pct"].median().to_dict()

df["roce_rating"] = df.apply(
    lambda r: roce_rating(r["return_on_capital_employed_pct"], r["broad_sector"], sector_medians),
    axis=1
)

print(f"Total rows processed: {len(df)}")
print(df[[
    "company_id", "year", "broad_sector",
    "net_profit_margin_pct", "operating_profit_margin_pct",
    "return_on_equity_pct", "return_on_capital_employed_pct",
    "return_on_assets_pct", "roce_rating"
]].head(10))

print("\nNull counts per ratio:")
print(df[[
    "net_profit_margin_pct", "operating_profit_margin_pct",
    "return_on_equity_pct", "return_on_capital_employed_pct", "return_on_assets_pct"
]].isnull().sum())

mismatches = df[df["opm_mismatch_flag"]]
print(f"\nOPM mismatches found: {len(mismatches)} rows (logged, not printed individually)")
mismatches[[
    "company_id", "year", "broad_sector", "sales",
    "operating_profit", "opm_percentage", "operating_profit_margin_pct"
]].to_csv("output/day08_opm_mismatches.log", index=False)
print("Logged to output/day08_opm_mismatches.log")

print("\nROCE rating distribution (Financials only):")
print(df[df["broad_sector"] == "Financials"]["roce_rating"].value_counts())

print("\nROCE rating distribution (all sectors):")
print(df["roce_rating"].value_counts())

df.to_csv("output/day08_profitability_ratios.csv", index=False)
print("\nSaved to output/day08_profitability_ratios.csv")
