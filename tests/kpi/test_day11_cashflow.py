from src.analytics.cashflow_kpis import (
    normalize_year,
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_normalize_year_hyphen_format():
    assert normalize_year("Mar-13") == "Mar 2013"


def test_normalize_year_already_normal():
    assert normalize_year("Mar 2014") == "Mar 2014"


def test_normalize_year_ttm():
    assert normalize_year("TTM") is None


def test_fcf_normal():
    assert free_cash_flow(500, -200) == 300


def test_fcf_negative_allowed():
    assert free_cash_flow(100, -300) == -200


def test_cfo_quality_high():
    ratio, label = cfo_quality_score(120, 100)
    assert ratio == 1.2
    assert label == "High Quality"


def test_cfo_quality_accrual_risk():
    ratio, label = cfo_quality_score(30, 100)
    assert ratio == 0.3
    assert label == "Accrual Risk"


def test_cfo_quality_zero_pat():
    ratio, label = cfo_quality_score(100, 0)
    assert ratio is None
    assert label is None


def test_capex_intensity_asset_light():
    val, label = capex_intensity(-20, 1000)
    assert val == 2.0
    assert label == "Asset Light"


def test_capex_intensity_capital_intensive():
    val, label = capex_intensity(-150, 1000)
    assert val == 15.0
    assert label == "Capital Intensive"


def test_fcf_conversion_normal():
    assert fcf_conversion_rate(300, 400) == 75.0


def test_fcf_conversion_zero_op():
    assert fcf_conversion_rate(300, 0) is None


def test_capital_allocation_reinvestor():
    assert capital_allocation_pattern(100, -50, -30) == "Reinvestor"


def test_capital_allocation_distress():
    assert capital_allocation_pattern(-50, 100, 30) == "Distress Signal"


def test_capital_allocation_shareholder_returns():
    assert capital_allocation_pattern(100, -50, -30, cfo_pat_ratio=1.5) == "Shareholder Returns"