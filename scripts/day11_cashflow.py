import pandas as pd
from src.analytics.cashflow_kpis import (
    normalize_year,
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

pl = pd.read_excel("data/raw/profitandloss.xlsx", sheet_name="Profit & Loss", header=1)
cf = pd.read_excel("data/raw/cashflow.xlsx", sheet_name="Cash Flow", header=1)

import pandas as pd
from src.analytics.cashflow_kpis import (
    normalize_year,
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

pl = pd.read_excel("data/raw/profitandloss.xlsx", sheet_name="Profit & Loss", header=1)
cf = pd.read_excel("data/raw/cashflow.xlsx", sheet_name="Cash Flow", header=1)

cf["year_norm"] = cf["year"].apply(normalize_year)
cf = cf[cf["year_norm"].notna()].copy()
cf = cf.rename(columns={"year": "year_raw", "year_norm": "year"})


dupes = cf[cf.duplicated(subset=["company_id", "year"], keep=False)].sort_values(["company_id", "year"])
dupes.to_csv("output/day11_cashflow_duplicates.log", index=False)
print(f"Logged {len(dupes)} duplicate cashflow rows to output/day11_cashflow_duplicates.log")


cf = cf.drop_duplicates(subset=["company_id", "year"], keep="last")
print(f"Cashflow rows after dedup: {len(cf)}")

df = pl.merge(cf, on=["company_id", "year"], suffixes=("_pl", "_cf"))
print(f"Merged rows (P&L + Cashflow): {len(df)}")



df["free_cash_flow"] = df.apply(
    lambda r: free_cash_flow(r["operating_activity"], r["investing_activity"]), axis=1
)


capex_result = df.apply(
    lambda r: capex_intensity(r["investing_activity"], r["sales"]), axis=1
)
df["capex_intensity_pct"] = capex_result.apply(lambda x: x[0])
df["capex_intensity_label"] = capex_result.apply(lambda x: x[1])


df["fcf_conversion_rate"] = df.apply(
    lambda r: fcf_conversion_rate(r["free_cash_flow"], r["operating_profit"]), axis=1
)


df = df.sort_values(["company_id", "year"])
cfo_quality_results = []
for company_id, group in df.groupby("company_id"):
    group = group.sort_values("year")
    avg_cfo = group["operating_activity"].tail(5).mean()
    avg_pat = group["net_profit"].tail(5).mean()
    ratio, label = cfo_quality_score(avg_cfo, avg_pat)
    cfo_quality_results.append({"company_id": company_id, "cfo_quality_ratio": ratio, "cfo_quality_label": label})

cfo_quality_df = pd.DataFrame(cfo_quality_results)
df = df.merge(cfo_quality_df, on="company_id", how="left")

df["capital_allocation_pattern"] = df.apply(
    lambda r: capital_allocation_pattern(
        r["operating_activity"], r["investing_activity"], r["financing_activity"],
        cfo_pat_ratio=r["cfo_quality_ratio"]
    ),
    axis=1
)

print(df[[
    "company_id", "year", "free_cash_flow", "capex_intensity_label",
    "fcf_conversion_rate", "cfo_quality_label", "capital_allocation_pattern"
]].head(10))

print("\nCapital allocation pattern distribution:")
print(df["capital_allocation_pattern"].value_counts())

print("\nCapEx intensity distribution:")
print(df["capex_intensity_label"].value_counts())

# Save capital_allocation.csv as per sprint doc spec
df["cfo_sign"] = df["operating_activity"].apply(lambda x: "+" if x > 0 else "-")
df["cfi_sign"] = df["investing_activity"].apply(lambda x: "+" if x > 0 else "-")
df["cff_sign"] = df["financing_activity"].apply(lambda x: "+" if x > 0 else "-")

capital_alloc_csv = df[["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "capital_allocation_pattern"]].rename(
    columns={"capital_allocation_pattern": "pattern_label"}
)
capital_alloc_csv.to_csv("output/capital_allocation.csv", index=False)
print("\nSaved to output/capital_allocation.csv")

df.to_csv("output/day11_cashflow_kpis.csv", index=False)
print("Saved to output/day11_cashflow_kpis.csv")