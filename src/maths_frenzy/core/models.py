"""Domain models shared by every interface."""

from __future__ import annotations

import operator
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

__all__ = ["Level", "Operation", "Question"]


class Level(str, Enum):
    """Difficulty level. Controls the range of the random operands."""

    BEGINNER = "beginner"
    ADVANCED = "advanced"
    MASTER = "master"

    @property
    def max_operand(self) -> int:
        """Operands are drawn from ``-max_operand`` to ``+max_operand``."""
        return _MAX_OPERAND[self]

    @property
    def label(self) -> str:
        return self.value.capitalize()

    @property
    def description(self) -> str:
        return f"numbers from -{self.max_operand} to {self.max_operand}"


_MAX_OPERAND: dict[Level, int] = {
    Level.BEGINNER: 20,
    Level.ADVANCED: 50,
    Level.MASTER: 100,
}


class Operation(str, Enum):
    """An arithmetic operation."""

    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

    @property
    def symbol(self) -> str:
        return _SYMBOLS[self]

    @property
    def label(self) -> str:
        return self.value.capitalize()

    def apply(self, left: float, right: float) -> float:
        """Apply the operation. Division by zero raises ``ZeroDivisionError``."""
        return _FUNCTIONS[self](left, right)


_SYMBOLS: dict[Operation, str] = {
    Operation.ADDITION: "+",
    Operation.SUBTRACTION: "\u2212",
    Operation.MULTIPLICATION: "\u00d7",
    Operation.DIVISION: "\u00f7",
}

_FUNCTIONS: dict[Operation, Callable[[float, float], float]] = {
    Operation.ADDITION: operator.add,
    Operation.SUBTRACTION: operator.sub,
    Operation.MULTIPLICATION: operator.mul,
    Operation.DIVISION: operator.truediv,
}

#: Division answers are rounded to this many decimal places.
DIVISION_PRECISION = 2


@dataclass(frozen=True, slots=True)
class Question:
    """A single arithmetic question."""

    left: int
    right: int
    operation: Operation

    def __post_init__(self) -> None:
        if self.operation is Operation.DIVISION and self.right == 0:
            raise ValueError("Division questions cannot have a zero divisor.")

    @property
    def expression(self) -> str:
        """Human readable expression, e.g. ``5 + (-3)``."""
        right = f"({self.right})" if self.right < 0 else str(self.right)
        return f"{self.left} {self.operation.symbol} {right}"

    @property
    def text(self) -> str:
        return f"What is {self.expression}?"

    @property
    def answer(self) -> float:
        """The correct answer (division is rounded to two decimal places)."""
        value = self.operation.apply(self.left, self.right)
        if self.operation is Operation.DIVISION:
            return round(value, DIVISION_PRECISION)
        return value

    def is_correct(self, value: float) -> bool:
        """Whether ``value`` matches the answer once rounded to two decimals."""
        return round(value, DIVISION_PRECISION) == self.answer
