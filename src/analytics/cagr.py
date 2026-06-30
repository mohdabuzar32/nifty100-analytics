import pandas as pd


def calculate_cagr(start_value, end_value, n_years):
    if n_years is None or n_years <= 0:
        return None, "INSUFFICIENT"

    if pd.isna(start_value) or pd.isna(end_value):
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value > 0:
        cagr = (((end_value / start_value) ** (1 / n_years)) - 1) * 100
        return round(cagr, 2), None

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def get_cagr_for_window(series_sorted_by_year, window_years):
    """
    series_sorted_by_year: list/Series of values sorted oldest->newest
    window_years: 3, 5, or 10
    Returns (cagr_value, flag)
    """
    if len(series_sorted_by_year) <= window_years:
        return None, "INSUFFICIENT"

    start_value = series_sorted_by_year[-(window_years + 1)]
    end_value = series_sorted_by_year[-1]
    return calculate_cagr(start_value, end_value, window_years)