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
 # ---------------- Day 9: Leverage & Efficiency Ratios ----------------

def debt_to_equity(borrowings, equity_capital, reserves):
    denom = equity_capital + reserves
    if denom <= 0 or pd.isna(denom):
        return None
    if borrowings == 0:
        return 0.0
    return round(borrowings / denom, 2)

def high_leverage_flag(de_ratio, broad_sector):
    if de_ratio is None:
        return False
    return de_ratio > 5 and broad_sector != "Financials"

def interest_coverage_ratio(operating_profit, other_income, interest):
    if interest == 0 or pd.isna(interest):
        return None, "Debt Free"
    if pd.isna(operating_profit) or pd.isna(other_income):
        return None, None
    icr = round((operating_profit + other_income) / interest, 2)
    return icr, None

def icr_warning_flag(icr):
    if icr is None:
        return False
    return icr < 1.5

def net_debt(borrowings, investments):
    return borrowings - investments

def asset_turnover(sales, total_assets):
    if total_assets == 0 or pd.isna(total_assets):
        return None
    return round(sales / total_assets, 2)   