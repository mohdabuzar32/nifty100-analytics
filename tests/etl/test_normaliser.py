import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.etl.normaliser import normalize_year, normalize_ticker


# ---------- normalize_year tests (20+) ----------

def test_year_dec_2012():
    assert normalize_year("Dec 2012") == 2012


def test_year_mar_2014():
    assert normalize_year("Mar 2014") == 2014


def test_year_sep_2024():
    assert normalize_year("Sep 2024") == 2024


def test_year_jun_2015():
    assert normalize_year("Jun 2015") == 2015


def test_year_mar_hyphen_13():
    assert normalize_year("Mar-13") == 2013


def test_year_mar_hyphen_24():
    assert normalize_year("Mar-24") == 2024


def test_year_ttm():
    assert normalize_year("TTM") == "TTM"


def test_year_ttm_lowercase():
    assert normalize_year("ttm") == "TTM"


def test_year_mar_2016_9m():
    assert normalize_year("Mar 2016 9m") == 2016


def test_year_mar_2023_15():
    assert normalize_year("Mar 2023 15") == 2023


def test_year_plain_int_string():
    assert normalize_year("2013") == 2013


def test_year_plain_float_string():
    assert normalize_year("2024.5") == 2024


def test_year_none():
    assert normalize_year(None) is None


def test_year_empty_string():
    assert normalize_year("") is None


def test_year_nan_string():
    assert normalize_year("nan") is None


def test_year_whitespace_padded():
    assert normalize_year("  Mar 2014  ") == 2014


def test_year_dec_2023():
    assert normalize_year("Dec 2023") == 2023


def test_year_sep_2011():
    assert normalize_year("Sep 2011") == 2011


def test_year_mar_2011():
    assert normalize_year("Mar 2011") == 2011


def test_year_jun_2013():
    assert normalize_year("Jun 2013") == 2013


def test_year_mar_hyphen_format_all_months():
    assert normalize_year("Mar-16") == 2016
    assert normalize_year("Mar-19") == 2019
    assert normalize_year("Mar-22") == 2022


def test_year_unparseable_returns_none():
    assert normalize_year("not a year") is None


def test_year_integer_input():
    assert normalize_year(2020) == 2020


# ---------- normalize_ticker tests (15+) ----------

def test_ticker_simple_uppercase():
    assert normalize_ticker("ABB") == "ABB"


def test_ticker_lowercase_to_upper():
    assert normalize_ticker("hdfcbank") == "HDFCBANK"


def test_ticker_mixed_case():
    assert normalize_ticker("InfY") == "INFY"


def test_ticker_leading_trailing_spaces():
    assert normalize_ticker("  TCS  ") == "TCS"


def test_ticker_internal_space_removed():
    assert normalize_ticker("HDFC BANK") == "HDFCBANK"


def test_ticker_with_hyphen_preserved():
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"


def test_ticker_with_ampersand_preserved():
    assert normalize_ticker("m&m") == "M&M"


def test_ticker_none_input():
    assert normalize_ticker(None) is None


def test_ticker_empty_string():
    assert normalize_ticker("") is None


def test_ticker_nan_string():
    assert normalize_ticker("nan") is None


def test_ticker_already_clean():
    assert normalize_ticker("RELIANCE") == "RELIANCE"


def test_ticker_numbers_in_ticker():
    assert normalize_ticker("abc123") == "ABC123"


def test_ticker_tabs_and_newlines():
    assert normalize_ticker("\tTCS\n") == "TCS"


def test_ticker_multiple_internal_spaces():
    assert normalize_ticker("BAJAJ   FINSV") == "BAJAJFINSV"


def test_ticker_single_character():
    assert normalize_ticker("a") == "A"