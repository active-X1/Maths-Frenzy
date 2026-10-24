"""Interface-agnostic game logic. Pure Python, no third-party dependencies."""

from .calculator import CalculatorError, calculate, evaluate
from .models import Level, Operation, Question
from .numbers import InvalidNumberError, format_number, parse_number
from .questions import QuestionGenerator
from .session import (
    AnswerRecord,
    GameConfig,
    GameFinishedError,
    GameResult,
    GameSession,
    Outcome,
)

__all__ = [
    "AnswerRecord",
    "CalculatorError",
    "GameConfig",
    "GameFinishedError",
    "GameResult",
    "GameSession",
    "InvalidNumberError",
    "Level",
    "Operation",
    "Outcome",
    "Question",
    "QuestionGenerator",
    "calculate",
    "evaluate",
    "format_number",
    "parse_number",
]
