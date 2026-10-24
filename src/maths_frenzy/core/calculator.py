"""A safe arithmetic evaluator and a two-operand calculator.

The expression evaluator parses input with :mod:`ast` and only walks a small
whitelist of node types, so it never executes arbitrary code (unlike ``eval``).
"""

from __future__ import annotations

import ast
import math
import operator
import re
from collections.abc import Callable

from .models import Operation

__all__ = ["CalculatorError", "calculate", "evaluate"]

MAX_EXPRESSION_LENGTH = 200
MAX_EXPONENT = 1000
MAX_INT_BITS = 4096  # keeps results printable and computation instant

_BINARY: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_CHAR_MAP = str.maketrans({"\u00d7": "*", "\u00f7": "/", "\u2212": "-", "^": "**"})
_LEADING_ZEROS = re.compile(r"(?<![\d.])0+(?=\d)")


class CalculatorError(ValueError):
    """Raised for invalid expressions and impossible calculations."""


def evaluate(expression: str) -> int | float:
    """Safely evaluate an arithmetic expression.

    Supports ``+ - * / // % **`` (also ``\u00d7 \u00f7 \u2212 ^``), unary signs and parentheses.

    >>> evaluate("2 * (3 + 4)")
    14
    >>> evaluate("10 / 4")
    2.5
    """
    text = _LEADING_ZEROS.sub("", expression.strip().translate(_CHAR_MAP))
    if not text:
        raise CalculatorError("Enter an expression.")
    if len(text) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError("Expression is too long.")
    try:
        tree = ast.parse(text, mode="eval")
        result = _eval(tree.body)
    except CalculatorError:
        raise
    except (SyntaxError, ValueError, RecursionError):
        raise CalculatorError("Invalid expression.") from None
    except ZeroDivisionError:
        raise CalculatorError("Cannot divide by zero.") from None
    except OverflowError:
        raise CalculatorError("The result is too large.") from None
    if isinstance(result, float) and not math.isfinite(result):
        raise CalculatorError("The result is too large.")
    return result


def calculate(left: float, right: float, operation: Operation) -> float:
    """Apply a single operation to two numbers."""
    try:
        result = operation.apply(left, right)
    except ZeroDivisionError:
        raise CalculatorError("Cannot divide by zero.") from None
    except OverflowError:
        raise CalculatorError("The result is too large.") from None
    if not math.isfinite(result):
        raise CalculatorError("The result is too large.")
    return result


def _eval(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant):
        value = node.value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left = _eval(node.left)
        right = _eval(node.right)
        if isinstance(node.op, ast.Pow):
            _check_power(left, right)
        result = _BINARY[type(node.op)](left, right)
        if isinstance(result, complex):
            raise CalculatorError("The result is not a real number.")
        if isinstance(result, int) and result.bit_length() > MAX_INT_BITS:
            raise CalculatorError("The result is too large.")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))
    raise CalculatorError("Only numbers, + - \u00d7 \u00f7 ^ % and parentheses are allowed.")


def _check_power(base: float, exponent: float) -> None:
    if abs(exponent) > MAX_EXPONENT:
        raise CalculatorError("The exponent is too large.")
    if (
        isinstance(base, int)
        and isinstance(exponent, int)
        and exponent > 0
        and abs(base).bit_length() * exponent > MAX_INT_BITS
    ):
        raise CalculatorError("The result is too large.")
