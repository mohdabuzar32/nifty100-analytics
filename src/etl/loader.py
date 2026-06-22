import os
import pandas as pd
from src.etl.normaliser import normalize_year, normalize_ticker

RAW_DIR = "data/raw"

CORE_FILES = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
    "analysis": "analysis.xlsx",
}

SUPPLEMENTARY_FILES = {
    "stock_prices": "stock_prices.xlsx",
    "sectors": "sectors.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "market_cap": "market_cap.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
}


def load_core_file(filename):
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_excel(path, header=1)
    return df


def load_supplementary_file(filename):
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_excel(path)
    return df


def apply_normalisation(df):
    if "company_id" in df.columns:
        df["company_id"] = df["company_id"].apply(normalize_ticker)
    if "id" in df.columns and df["id"].dtype == object:
        df["id"] = df["id"].apply(normalize_ticker)

    year_col = None
    if "year" in df.columns:
        year_col = "year"
    elif "Year" in df.columns:
        year_col = "Year"

    if year_col:
        df[year_col] = df[year_col].apply(normalize_year)

    return df


def load_all_tables():
    tables = {}

    for table_name, filename in CORE_FILES.items():
        df = load_core_file(filename)
        df = apply_normalisation(df)
        tables[table_name] = df
        print(f"Loaded {table_name}: {df.shape[0]} rows, {df.shape[1]} columns")

    for table_name, filename in SUPPLEMENTARY_FILES.items():
        df = load_supplementary_file(filename)
        df = apply_normalisation(df)
        tables[table_name] = df
        print(f"Loaded {table_name}: {df.shape[0]} rows, {df.shape[1]} columns")

    return tables


if __name__ == "__main__":
    tables = load_all_tables()
    print("\nAll 12 tables loaded successfully.")
    print("Table names:", list(tables.keys()))