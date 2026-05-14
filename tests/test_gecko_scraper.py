"""Unit tests for _parse_price() — ingen Selenium."""
from klinik.gecko.scraper import _parse_price


def test_plain_integer() -> None:
    assert _parse_price("4500 DKK") == 4500.0


def test_thousands_separator() -> None:
    assert _parse_price("1.700 DKK") == 1700.0


def test_large_thousands() -> None:
    assert _parse_price("15.000 DKK") == 15000.0


def test_range_no_spaces() -> None:
    assert _parse_price("800-1000 DKK") == 900.0


def test_range_larger() -> None:
    assert _parse_price("1000-1250 DKK") == 1125.0


def test_fra_lowercase() -> None:
    assert _parse_price("fra 600 DKK") == 600.0


def test_fra_uppercase() -> None:
    assert _parse_price("Fra 2500 DKK") == 2500.0


def test_only_dkk_returns_zero() -> None:
    assert _parse_price("DKK") == 0.0


def test_empty_returns_zero() -> None:
    assert _parse_price("") == 0.0


def test_strips_html_tags() -> None:
    assert _parse_price("<span>1.900</span> DKK") == 1900.0
