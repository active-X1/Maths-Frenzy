"""Game session state machine.

A :class:`GameSession` owns everything about one round of play (the questions,
the score and the answer history) but knows nothing about timers or widgets.
Each interface drives it by calling :meth:`GameSession.submit` for an answer
and :meth:`GameSession.time_out` when the clock runs out.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from .models import Level, Operation, Question
from .numbers import parse_number
from .questions import QuestionGenerator

__all__ = [
    "AnswerRecord",
    "GameConfig",
    "GameFinishedError",
    "GameResult",
    "GameSession",
    "Outcome",
]

DEFAULT_QUESTION_COUNT = 20
DEFAULT_SECONDS_PER_QUESTION = 20


class GameFinishedError(RuntimeError):
    """Raised when answering a question after the game is over."""


class Outcome(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class GameConfig:
    """Settings for one round. ``seconds_per_question=None`` disables the timer."""

    level: Level
    operation: Operation
    question_count: int = DEFAULT_QUESTION_COUNT
    seconds_per_question: int | None = DEFAULT_SECONDS_PER_QUESTION

    def __post_init__(self) -> None:
        if self.question_count < 1:
            raise ValueError("question_count must be at least 1")
        if self.seconds_per_question is not None and self.seconds_per_question < 1:
            raise ValueError("seconds_per_question must be at least 1 (or None)")


@dataclass(frozen=True)
class AnswerRecord:
    """The result of one question."""

    question: Question
    given: float | None
    outcome: Outcome

    @property
    def correct(self) -> bool:
        return self.outcome is Outcome.CORRECT


@dataclass(frozen=True)
class GameResult:
    """Summary of a finished (or abandoned) game."""

    records: tuple[AnswerRecord, ...]
    total: int

    @property
    def score(self) -> int:
        return sum(record.correct for record in self.records)

    @property
    def accuracy(self) -> float:
        """Fraction of the total questions answered correctly (0.0 to 1.0)."""
        return self.score / self.total if self.total else 0.0

    @property
    def mistakes(self) -> tuple[AnswerRecord, ...]:
        return tuple(record for record in self.records if not record.correct)

    @property
    def rank(self) -> str:
        accuracy = self.accuracy
        if accuracy >= 0.9:
            return "Maths Wizard"
        if accuracy >= 0.7:
            return "Sharp Mind"
        if accuracy >= 0.5:
            return "Getting There"
        return "Keep Practising"


class GameSession:
    """One round of Maths Frenzy."""

    def __init__(
        self,
        config: GameConfig,
        *,
        player: str = "Player",
        rng: random.Random | None = None,
    ) -> None:
        self.config = config
        self.player = player
        self._generator = QuestionGenerator(config.level, config.operation, rng)
        self._records: list[AnswerRecord] = []
        self._current: Question | None = self._generator.next_question()

    @property
    def current(self) -> Question | None:
        """The question awaiting an answer, or ``None`` once the game is over."""
        return self._current

    @property
    def number(self) -> int:
        """1-based number of the current question (equals the total when finished)."""
        return min(len(self._records) + 1, self.config.question_count)

    @property
    def score(self) -> int:
        return sum(record.correct for record in self._records)

    @property
    def finished(self) -> bool:
        return self._current is None

    @property
    def records(self) -> tuple[AnswerRecord, ...]:
        return tuple(self._records)

    def submit(self, raw: str) -> AnswerRecord:
        """Submit an answer for the current question.

        Raises:
            InvalidNumberError: if ``raw`` is not a number. The game state is
                unchanged, so the player may simply try again.
            GameFinishedError: if the game is already over.
        """
        question = self._require_current()
        value = parse_number(raw)
        outcome = Outcome.CORRECT if question.is_correct(value) else Outcome.INCORRECT
        return self._record(question, value, outcome)

    def time_out(self) -> AnswerRecord:
        """Record the current question as unanswered because time ran out."""
        question = self._require_current()
        return self._record(question, None, Outcome.TIMEOUT)

    def result(self) -> GameResult:
        return GameResult(records=tuple(self._records), total=self.config.question_count)

    def _require_current(self) -> Question:
        if self._current is None:
            raise GameFinishedError("The game is already finished.")
        return self._current

    def _record(self, question: Question, given: float | None, outcome: Outcome) -> AnswerRecord:
        record = AnswerRecord(question, given, outcome)
        self._records.append(record)
        if len(self._records) >= self.config.question_count:
            self._current = None
        else:
            self._current = self._generator.next_question()
        return record
