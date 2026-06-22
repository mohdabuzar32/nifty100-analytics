import os
import pandas as pd
from src.etl.loader import load_all_tables

OUTPUT_DIR = "output"
KNOWN_SECTORS = [
    "Industrials", "Energy", "Materials", "Healthcare", "Financials",
    "Consumer Discretionary", "Communication Services", "Consumer Staples",
    "Real Estate", "Information Technology"
]


def add_failure(failures, rule, severity, table, row_id, company_id, year, detail):
    failures.append({
        "rule": rule,
        "severity": severity,
        "table": table,
        "row_id": row_id,
        "company_id": company_id,
        "year": year,
        "detail": detail
    })


def dq01_pk_uniqueness(tables, failures):
    for table_name, df in tables.items():
        if "id" not in df.columns:
            continue
        dup_ids = df[df["id"].duplicated(keep=False)]
        for _, row in dup_ids.iterrows():
            add_failure(failures, "DQ-01", "CRITICAL", table_name, row["id"],
                        row.get("company_id"), row.get("year"), "Duplicate primary key id")


def dq02_composite_pk(tables, failures):
    for table_name, df in tables.items():
        if "company_id" not in df.columns:
            continue
        year_col = "year" if "year" in df.columns else ("Year" if "Year" in df.columns else None)
        if year_col is None:
            continue
        dup_mask = df.duplicated(subset=["company_id", year_col], keep=False)
        dup_rows = df[dup_mask]
        for _, row in dup_rows.iterrows():
            add_failure(failures, "DQ-02", "CRITICAL", table_name, row.get("id"),
                        row["company_id"], row[year_col],
                        "Duplicate (company_id, year) combination")


def dq03_fk_integrity(tables, failures):
    valid_companies = set(tables["companies"]["id"].dropna())
    for table_name, df in tables.items():
        if table_name == "companies" or "company_id" not in df.columns:
            continue
        invalid = df[~df["company_id"].isin(valid_companies)]
        for _, row in invalid.iterrows():
            year_col = "year" if "year" in df.columns else ("Year" if "Year" in df.columns else None)
            add_failure(failures, "DQ-03", "CRITICAL", table_name, row.get("id"),
                        row["company_id"], row.get(year_col) if year_col else None,
                        f"company_id '{row['company_id']}' not found in companies table")


def dq04_bs_balance(tables, failures):
    df = tables.get("balancesheet")
    if df is None:
        return
    diff_pct = (df["total_liabilities"] - df["total_assets"]).abs() / df["total_assets"].replace(0, 1).abs()
    bad = df[diff_pct > 0.01]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-04", "WARNING", "balancesheet", row.get("id"),
                    row["company_id"], row["year"],
                    f"total_liabilities ({row['total_liabilities']}) != total_assets ({row['total_assets']})")


def dq05_opm_crosscheck(tables, failures):
    df = tables.get("profitandloss")
    if df is None:
        return
    valid = df.dropna(subset=["sales", "operating_profit", "opm_percentage"])
    valid = valid[valid["sales"] != 0]
    calc_opm = (valid["operating_profit"] / valid["sales"]) * 100
    diff = (calc_opm - valid["opm_percentage"]).abs()
    bad = valid[diff > 5]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-05", "WARNING", "profitandloss", row.get("id"),
                    row["company_id"], row["year"],
                    f"opm_percentage ({row['opm_percentage']}) inconsistent with operating_profit/sales")


def dq06_positive_sales(tables, failures):
    df = tables.get("profitandloss")
    if df is None:
        return
    bad = df[df["sales"] < 0]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-06", "CRITICAL", "profitandloss", row.get("id"),
                    row["company_id"], row["year"], f"Negative sales: {row['sales']}")


def dq07_net_cash_flow(tables, failures):
    df = tables.get("cashflow")
    if df is None:
        return
    valid = df.dropna(subset=["operating_activity", "investing_activity", "financing_activity", "net_cash_flow"])
    calc_net = valid["operating_activity"] + valid["investing_activity"] + valid["financing_activity"]
    diff = (calc_net - valid["net_cash_flow"]).abs()
    bad = valid[diff > 1]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-07", "WARNING", "cashflow", row.get("id"),
                    row["company_id"], row["year"], "net_cash_flow does not match sum of activities")


def dq08_eps_sign(tables, failures):
    df = tables.get("profitandloss")
    if df is None:
        return
    valid = df.dropna(subset=["net_profit", "eps"])
    bad = valid[((valid["net_profit"] < 0) & (valid["eps"] > 0)) | ((valid["net_profit"] > 0) & (valid["eps"] < 0))]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-08", "WARNING", "profitandloss", row.get("id"),
                    row["company_id"], row["year"], "eps sign inconsistent with net_profit sign")


def dq09_tax_rate_range(tables, failures):
    df = tables.get("profitandloss")
    if df is None:
        return
    valid = df.dropna(subset=["tax_percentage"])
    bad = valid[(valid["tax_percentage"] < -100) | (valid["tax_percentage"] > 100)]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-09", "WARNING", "profitandloss", row.get("id"),
                    row["company_id"], row["year"], f"tax_percentage out of range: {row['tax_percentage']}")


def dq10_dividend_cap(tables, failures):
    df = tables.get("profitandloss")
    if df is None:
        return
    valid = df.dropna(subset=["dividend_payout"])
    bad = valid[valid["dividend_payout"] > 200]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-10", "WARNING", "profitandloss", row.get("id"),
                    row["company_id"], row["year"], f"dividend_payout exceeds 200%: {row['dividend_payout']}")


def dq11_valid_url(tables, failures):
    df = tables.get("documents")
    if df is not None:
        valid = df.dropna(subset=["Annual_Report"])
        bad = valid[~valid["Annual_Report"].str.startswith("http")]
        for _, row in bad.iterrows():
            add_failure(failures, "DQ-11", "WARNING", "documents", row.get("id"),
                        row["company_id"], row.get("Year"), "Annual_Report URL does not start with http")

    df2 = tables.get("companies")
    if df2 is not None:
        valid2 = df2.dropna(subset=["website"])
        bad2 = valid2[~valid2["website"].str.startswith("http")]
        for _, row in bad2.iterrows():
            add_failure(failures, "DQ-11", "WARNING", "companies", row.get("id"),
                        row.get("id"), None, "website URL does not start with http")


def dq12_year_range(tables, failures):
    for table_name, df in tables.items():
        year_col = "year" if "year" in df.columns else ("Year" if "Year" in df.columns else None)
        if year_col is None:
            continue
        numeric_years = pd.to_numeric(df[year_col], errors="coerce")
        bad = df[(numeric_years.notna()) & ((numeric_years < 2000) | (numeric_years > 2026))]
        for _, row in bad.iterrows():
            add_failure(failures, "DQ-12", "CRITICAL", table_name, row.get("id"),
                        row.get("company_id"), row[year_col], f"year out of valid range: {row[year_col]}")


def dq13_null_core_fields(tables, failures):
    for table_name, df in tables.items():
        if "id" in df.columns:
            bad = df[df["id"].isnull()]
            for _, row in bad.iterrows():
                add_failure(failures, "DQ-13", "CRITICAL", table_name, None,
                            row.get("company_id"), None, "Null id field")
        if "company_id" in df.columns:
            bad = df[df["company_id"].isnull()]
            for _, row in bad.iterrows():
                add_failure(failures, "DQ-13", "CRITICAL", table_name, row.get("id"),
                            None, None, "Null company_id field")


def dq14_coverage_check(tables, failures):
    companies_df = tables.get("companies")
    if companies_df is None:
        return
    all_companies = set(companies_df["id"].dropna())
    pl_df = tables.get("profitandloss")
    if pl_df is None:
        return
    companies_with_data = set(pl_df["company_id"].dropna())
    missing = all_companies - companies_with_data
    for company_id in missing:
        add_failure(failures, "DQ-14", "WARNING", "profitandloss", None,
                    company_id, None, "Company has no profitandloss records")


def dq15_duplicate_rows(tables, failures):
    for table_name, df in tables.items():
        cols_to_check = [c for c in df.columns if c != "id"]
        dup_mask = df.duplicated(subset=cols_to_check, keep=False)
        dup_rows = df[dup_mask]
        for _, row in dup_rows.iterrows():
            year_col = "year" if "year" in df.columns else ("Year" if "Year" in df.columns else None)
            add_failure(failures, "DQ-15", "CRITICAL", table_name, row.get("id"),
                        row.get("company_id"), row.get(year_col) if year_col else None,
                        "Fully duplicate row (excluding id)")


def dq16_sector_validity(tables, failures):
    df = tables.get("sectors")
    if df is None:
        return
    bad = df[~df["broad_sector"].isin(KNOWN_SECTORS)]
    for _, row in bad.iterrows():
        add_failure(failures, "DQ-16", "WARNING", "sectors", row.get("id"),
                    row["company_id"], None, f"Unknown broad_sector: {row['broad_sector']}")


def run_all_validations(tables):
    failures = []

    dq01_pk_uniqueness(tables, failures)
    dq02_composite_pk(tables, failures)
    dq03_fk_integrity(tables, failures)
    dq04_bs_balance(tables, failures)
    dq05_opm_crosscheck(tables, failures)
    dq06_positive_sales(tables, failures)
    dq07_net_cash_flow(tables, failures)
    dq08_eps_sign(tables, failures)
    dq09_tax_rate_range(tables, failures)
    dq10_dividend_cap(tables, failures)
    dq11_valid_url(tables, failures)
    dq12_year_range(tables, failures)
    dq13_null_core_fields(tables, failures)
    dq14_coverage_check(tables, failures)
    dq15_duplicate_rows(tables, failures)
    dq16_sector_validity(tables, failures)

    return pd.DataFrame(failures)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    tables = load_all_tables()
    failures_df = run_all_validations(tables)

    output_path = os.path.join(OUTPUT_DIR, "validation_failures.csv")
    failures_df.to_csv(output_path, index=False)

    print(f"\nTotal DQ failures found: {len(failures_df)}")
    if len(failures_df) > 0:
        print("\nFailures by rule:")
        print(failures_df.groupby(["rule", "severity"]).size())
        critical_count = len(failures_df[failures_df["severity"] == "CRITICAL"])
        print(f"\nCRITICAL failures: {critical_count}")
    print(f"\nSaved to: {output_path}")