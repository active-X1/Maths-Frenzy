"""Random question generation."""

from __future__ import annotations

import random

from .models import Level, Operation, Question

__all__ = ["QuestionGenerator"]


class QuestionGenerator:
    """Generates an endless stream of questions for a level and operation.

    Pass a seeded :class:`random.Random` for reproducible output (useful in tests).
    """

    def __init__(
        self,
        level: Level,
        operation: Operation,
        rng: random.Random | None = None,
    ) -> None:
        self.level = level
        self.operation = operation
        self._rng = rng if rng is not None else random.Random()

    def next_question(self) -> Question:
        bound = self.level.max_operand
        left = self._rng.randint(-bound, bound)
        right = self._rng.randint(-bound, bound)
        if self.operation is Operation.DIVISION:
            while right == 0:
                right = self._rng.randint(-bound, bound)
        return Question(left, right, self.operation)
