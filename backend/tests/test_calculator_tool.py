import pytest

from app.tools.calculator_tool import CalculatorError, evaluate, extract_expression


def test_basic_arithmetic():
    assert evaluate("1 + 2 * 3") == 7


def test_parentheses_and_power():
    assert evaluate("(2 + 3) ** 2") == 25


def test_division_by_zero_raises():
    with pytest.raises(CalculatorError):
        evaluate("1 / 0")


def test_whitelisted_function():
    assert evaluate("abs(-5)") == 5


def test_disallows_arbitrary_names():
    with pytest.raises(CalculatorError):
        evaluate("__import__('os').system('echo hi')")


def test_disallows_attribute_access():
    with pytest.raises(CalculatorError):
        evaluate("().__class__")


def test_invalid_syntax_raises():
    with pytest.raises(CalculatorError):
        evaluate("2 +")


def test_extract_expression_finds_arithmetic():
    assert extract_expression("what is 1234 * 1.05?") == "1234 * 1.05"


def test_extract_expression_returns_none_for_prose():
    assert extract_expression("What was the revenue growth percentage?") is None
