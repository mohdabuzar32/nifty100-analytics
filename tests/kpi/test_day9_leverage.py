from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_warning_flag,
    net_debt,
    asset_turnover,
)


def test_de_normal():
    assert debt_to_equity(500, 100, 400) == 1.0


def test_de_debtfree_returns_zero():
    assert debt_to_equity(0, 100, 400) == 0.0


def test_de_negative_equity_returns_none():
    assert debt_to_equity(500, -100, -50) is None


def test_high_leverage_flag_true_non_financial():
    assert high_leverage_flag(6.0, "Industrials") is True


def test_high_leverage_flag_false_for_financials():
    assert high_leverage_flag(6.0, "Financials") is False


def test_icr_normal():
    icr, label = interest_coverage_ratio(300, 20, 80)
    assert icr == 4.0
    assert label is None


def test_icr_zero_interest_debtfree_label():
    icr, label = interest_coverage_ratio(300, 20, 0)
    assert icr is None
    assert label == "Debt Free"


def test_icr_warning_flag_low_icr():
    assert icr_warning_flag(1.2) is True


def test_icr_warning_flag_healthy_icr():
    assert icr_warning_flag(3.0) is False


def test_net_debt():
    assert net_debt(500, 150) == 350


def test_asset_turnover_normal():
    assert asset_turnover(1653, 907) == 1.82


def test_asset_turnover_zero_assets():
    assert asset_turnover(100, 0) is None