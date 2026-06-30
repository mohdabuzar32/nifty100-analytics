import pandas as pd
from src.analytics.cagr import get_cagr_for_window

pl = pd.read_excel("data/raw/profitandloss.xlsx", sheet_name="Profit & Loss", header=1)


pl = pl[pl["year"] != "TTM"].copy()

pl["year_num"] = pl["year"].str.extract(r"(\d{4})")[0].astype(int)
pl = pl.sort_values(["company_id", "year_num"])

results = []

for company_id, group in pl.groupby("company_id"):
    group = group.sort_values("year_num")
    revenue_series = group["sales"].tolist()
    pat_series = group["net_profit"].tolist()
    eps_series = group["eps"].tolist()
    latest_year = group["year"].iloc[-1]

    row = {"company_id": company_id, "year": latest_year}

    for label, series in [("revenue", revenue_series), ("pat", pat_series), ("eps", eps_series)]:
        for window in [3, 5, 10]:
            cagr, flag = get_cagr_for_window(series, window)
            row[f"{label}_cagr_{window}yr"] = cagr
            row[f"{label}_cagr_{window}yr_flag"] = flag

    results.append(row)

df = pd.DataFrame(results)

print(f"Total companies processed: {len(df)}")
print(df[["company_id", "year", "revenue_cagr_5yr", "revenue_cagr_5yr_flag",
          "pat_cagr_5yr", "pat_cagr_5yr_flag"]].head(10))

print("\nFlag distribution (Revenue 5yr CAGR):")
print(df["revenue_cagr_5yr_flag"].value_counts(dropna=False))

print("\nFlag distribution (PAT 5yr CAGR):")
print(df["pat_cagr_5yr_flag"].value_counts(dropna=False))

print("\nFlag distribution (Revenue 10yr CAGR):")
print(df["revenue_cagr_10yr_flag"].value_counts(dropna=False))

df.to_csv("output/day10_cagr_metrics.csv", index=False)
print("\nSaved to output/day10_cagr_metrics.csv")