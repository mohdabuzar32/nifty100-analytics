import pandas as pd


def normalize_year(year_str):
    """Convert 'Mar-13' style to 'Mar 2013' style; pass through if already in that format."""
    if pd.isna(year_str) or year_str == "TTM":
        return None
    year_str = str(year_str).strip()
    if "-" in year_str:
        mon, yr2 = year_str.split("-")
        yr2 = int(yr2)
        full_year = 2000 + yr2 if yr2 < 50 else 1900 + yr2
        return f"{mon} {full_year}"
    return year_str


def free_cash_flow(operating_activity, investing_activity):
    if pd.isna(operating_activity) or pd.isna(investing_activity):
        return None
    return round(operating_activity + investing_activity, 2)


def cfo_quality_score(avg_cfo, avg_pat):
    if avg_pat == 0 or pd.isna(avg_pat) or pd.isna(avg_cfo):
        return None, None
    ratio = avg_cfo / avg_pat
    if ratio > 1.0:
        label = "High Quality"
    elif ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
    return round(ratio, 2), label


def capex_intensity(investing_activity, sales):
    if sales == 0 or pd.isna(sales) or pd.isna(investing_activity):
        return None, None
    intensity = round((abs(investing_activity) / sales) * 100, 2)
    if intensity < 3:
        label = "Asset Light"
    elif intensity <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"
    return intensity, label


def fcf_conversion_rate(fcf, operating_profit):
    if operating_profit == 0 or pd.isna(operating_profit) or pd.isna(fcf):
        return None
    return round((fcf / operating_profit) * 100, 2)


def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    if pd.isna(cfo) or pd.isna(cfi) or pd.isna(cff):
        return None

    cfo_sign = "+" if cfo > 0 else "-"
    cfi_sign = "+" if cfi > 0 else "-"
    cff_sign = "+" if cff > 0 else "-"

    pattern = (cfo_sign, cfi_sign, cff_sign)

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"
    elif pattern == ("+", "+", "-"):
        return "Liquidating Assets"
    elif pattern == ("-", "+", "+"):
        return "Distress Signal"
    elif pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"
    elif pattern == ("+", "+", "+"):
        return "Cash Accumulator"
    elif pattern == ("-", "-", "-"):
        return "Pre-Revenue"
    elif pattern == ("+", "-", "+"):
        return "Mixed"
    else:
        return "Unclassified"