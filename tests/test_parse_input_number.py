from utils_number import parse_input_number


def test_simple_integer():
    assert parse_input_number('25000') == 25000.0


def test_with_comma_thousands():
    assert parse_input_number('25,000') == 25000.0


def test_with_dot_thousands_eu():
    assert parse_input_number('25.000') == 25000.0


def test_with_decimal_comma():
    assert parse_input_number('25.000,50') == 25000.5


def test_with_currency_symbols():
    assert parse_input_number('$25,000.00') == 25000.0


def test_empty_returns_none():
    assert parse_input_number('', 'costo') is None


def test_invalid_raises():
    import pytest
    with pytest.raises(ValueError):
        parse_input_number('abc', 'peso')
