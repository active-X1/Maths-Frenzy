"""Number parsing and formatting helpers shared by every interface."""

from __future__ import annotations

import math

__all__ = ["InvalidNumberError", "format_number", "parse_number"]

# Typographic minus signs people paste or type on phone keyboards.
_MINUS_SIGNS = str.maketrans({"\u2212": "-", "\u2013": "-"})


class InvalidNumberError(ValueError):
    """Raised when text cannot be interpreted as a finite number."""


def parse_number(raw: str) -> float:
    """Parse user input into a finite float.

    Raises:
        InvalidNumberError: if the text is empty, not numeric, or not finite.
    """
    text = raw.strip().translate(_MINUS_SIGNS)
    if not text:
        raise InvalidNumberError("Please enter a number.")
    if "_" in text:
        raise InvalidNumberError(f"'{raw.strip()}' is not a valid number.")
    try:
        value = float(text)
    except ValueError:
        raise InvalidNumberError(f"'{raw.strip()}' is not a valid number.") from None
    if not math.isfinite(value):
        raise InvalidNumberError(f"'{raw.strip()}' is not a valid number.")
    return value


def format_number(value: float, *, precision: int = 10) -> str:
    """Format a number for display: ``8.0`` -> ``8`` and ``0.1 + 0.2`` -> ``0.3``."""
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(value):
        return str(value)
    if value.is_integer() and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.{precision}g}"
