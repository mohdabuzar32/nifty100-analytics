from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    roce_rating,
)


def test_npm_normal():
    assert net_profit_margin(145, 1653) == 8.77


def test_npm_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_roe_normal():
    assert return_on_equity(145, 21, 626) == 22.41


def test_roe_negative_equity():
    assert return_on_equity(100, -50, -20) is None


def test_roa_normal():
    assert return_on_assets(145, 907) == 15.99


def test_roa_zero_assets():
    assert return_on_assets(100, 0) is None


def test_opm_cross_check_match():
    result, mismatch = operating_profit_margin(202, 1653, 12.0)
    assert result == 12.22
    assert mismatch is False


def test_opm_cross_check_mismatch():
    result, mismatch = operating_profit_margin(202, 1653, 5.0)
    assert mismatch is True


def test_roce_rating_financials_above():
    medians = {"Financials": 5.0}
    assert roce_rating(8.0, "Financials", medians) == "Above Sector Benchmark"


def test_roce_rating_non_financials_absolute():
    medians = {"Financials": 5.0}
    assert roce_rating(20.0, "Energy", medians) == "Above Sector Benchmark"