import pandas as pd

def net_profit_margin(net_profit, sales):
    if sales == 0 or pd.isna(sales):
        return None
    return round((net_profit / sales) * 100, 2)

def operating_profit_margin(operating_profit, sales, opm_reported):
    if sales == 0 or pd.isna(sales):
        return None, False
    computed = round((operating_profit / sales) * 100, 2)
    mismatch = pd.notna(opm_reported) and abs(computed - opm_reported) > 1
    return computed, mismatch

def return_on_equity(net_profit, equity_capital, reserves):
    denom = equity_capital + reserves
    if denom <= 0 or pd.isna(denom):
        return None
    return round((net_profit / denom) * 100, 2)

def return_on_capital_employed(ebit, equity_capital, reserves, borrowings, broad_sector=None):
    denom = equity_capital + reserves + borrowings
    if denom <= 0 or pd.isna(denom):
        return None
    return round((ebit / denom) * 100, 2)

def return_on_assets(net_profit, total_assets):
    if total_assets == 0 or pd.isna(total_assets):
        return None
    return round((net_profit / total_assets) * 100, 2)
def roce_rating(roce, broad_sector, sector_medians):
    if roce is None:
        return None
    if broad_sector == "Financials":
        benchmark = sector_medians.get("Financials")
    else:
        benchmark = 15.0  # absolute threshold for non-Financials
    if benchmark is None or pd.isna(benchmark):
        return None
    if roce >= benchmark * 1.2:
        return "Above Sector Benchmark"
    elif roce <= benchmark * 0.8:
        return "Below Sector Benchmark"
    else:
        return "In Line with Benchmark"