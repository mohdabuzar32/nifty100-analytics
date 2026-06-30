import pandas as pd
from src.analytics.cagr import calculate_cagr, get_cagr_for_window


def test_cagr_normal_positive_to_positive():
    cagr, flag = calculate_cagr(100, 200, 5)
    assert flag is None
    assert cagr == 14.87


def test_cagr_turnaround_negative_to_positive():
    cagr, flag = calculate_cagr(-50, 100, 3)
    assert cagr is None
    assert flag == "TURNAROUND"


def test_cagr_decline_to_loss():
    cagr, flag = calculate_cagr(100, -50, 3)
    assert cagr is None
    assert flag == "DECLINE_TO_LOSS"


def test_cagr_both_negative():
    cagr, flag = calculate_cagr(-100, -50, 3)
    assert cagr is None
    assert flag == "BOTH_NEGATIVE"


def test_cagr_zero_base():
    cagr, flag = calculate_cagr(0, 100, 3)
    assert cagr is None
    assert flag == "ZERO_BASE"


def test_cagr_insufficient_data_window():
    series = [100, 110, 120]
    cagr, flag = get_cagr_for_window(series, 5)
    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_cagr_window_normal():
    series = [100, 110, 121, 133, 146, 161]
    cagr, flag = get_cagr_for_window(series, 5)
    assert flag is None
    assert cagr == round(((161 / 100) ** (1 / 5) - 1) * 100, 2)


def test_cagr_insufficient_zero_years():
    cagr, flag = calculate_cagr(100, 200, 0)
    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_cagr_nan_value_insufficient():
    cagr, flag = calculate_cagr(pd.NA, 200, 5)
    assert cagr is None
    assert flag == "INSUFFICIENT"


def test_cagr_realistic_revenue_3yr():
    cagr, flag = calculate_cagr(1653, 2289, 3)
    assert flag is None
    assert cagr == round(((2289 / 1653) ** (1 / 3) - 1) * 100, 2)