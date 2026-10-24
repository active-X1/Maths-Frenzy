import random
import unittest

from maths_frenzy.core import (
    GameConfig,
    GameFinishedError,
    GameSession,
    InvalidNumberError,
    Level,
    Operation,
    Outcome,
    format_number,
)


def make_session(count: int = 5) -> GameSession:
    config = GameConfig(Level.BEGINNER, Operation.ADDITION, question_count=count)
    return GameSession(config, rng=random.Random(3))


class ConfigTests(unittest.TestCase):
    def test_defaults_match_the_original_game(self) -> None:
        config = GameConfig(Level.BEGINNER, Operation.ADDITION)
        self.assertEqual((config.question_count, config.seconds_per_question), (20, 20))

    def test_validation(self) -> None:
        with self.assertRaises(ValueError):
            GameConfig(Level.BEGINNER, Operation.ADDITION, question_count=0)
        with self.assertRaises(ValueError):
            GameConfig(Level.BEGINNER, Operation.ADDITION, seconds_per_question=0)
        GameConfig(Level.BEGINNER, Operation.ADDITION, seconds_per_question=None)


class SessionTests(unittest.TestCase):
    def test_perfect_game(self) -> None:
        session = make_session(5)
        while not session.finished:
            session.submit(format_number(session.current.answer))  # type: ignore[union-attr]
        result = session.result()
        self.assertEqual((result.score, result.total, result.accuracy), (5, 5, 1.0))
        self.assertEqual(result.rank, "Maths Wizard")
        self.assertEqual(result.mistakes, ())
        self.assertIsNone(session.current)

    def test_counts_progress(self) -> None:
        session = make_session(3)
        self.assertEqual((session.number, session.score), (1, 0))
        session.submit(format_number(session.current.answer))  # type: ignore[union-attr]
        self.assertEqual((session.number, session.score), (2, 1))
        session.submit("999999")
        self.assertEqual((session.number, session.score), (3, 1))
        session.time_out()
        self.assertEqual((session.number, session.score), (3, 1))
        self.assertTrue(session.finished)

    def test_outcomes(self) -> None:
        session = make_session(3)
        right = session.submit(format_number(session.current.answer))  # type: ignore[union-attr]
        wrong = session.submit("999999")
        late = session.time_out()
        self.assertEqual([right.outcome, wrong.outcome, late.outcome],
                         [Outcome.CORRECT, Outcome.INCORRECT, Outcome.TIMEOUT])
        self.assertEqual(wrong.given, 999999.0)
        self.assertIsNone(late.given)
        self.assertEqual(len(session.result().mistakes), 2)

    def test_invalid_input_does_not_consume_the_question(self) -> None:
        session = make_session(3)
        before = session.current
        with self.assertRaises(InvalidNumberError):
            session.submit("abc")
        with self.assertRaises(InvalidNumberError):
            session.submit("")
        self.assertEqual(session.current, before)
        self.assertEqual(session.records, ())

    def test_cannot_answer_after_the_end(self) -> None:
        session = make_session(1)
        session.time_out()
        with self.assertRaises(GameFinishedError):
            session.submit("1")
        with self.assertRaises(GameFinishedError):
            session.time_out()

    def test_rank_thresholds(self) -> None:
        def rank_for(correct: int) -> str:
            session = make_session(10)
            for index in range(10):
                if index < correct:
                    session.submit(format_number(session.current.answer))  # type: ignore[union-attr]
                else:
                    session.time_out()
            return session.result().rank

        self.assertEqual(rank_for(10), "Maths Wizard")
        self.assertEqual(rank_for(9), "Maths Wizard")
        self.assertEqual(rank_for(7), "Sharp Mind")
        self.assertEqual(rank_for(5), "Getting There")
        self.assertEqual(rank_for(4), "Keep Practising")

    def test_partial_result_uses_full_total(self) -> None:
        session = make_session(4)
        session.submit(format_number(session.current.answer))  # type: ignore[union-attr]
        result = session.result()
        self.assertEqual((result.score, result.total, result.accuracy), (1, 4, 0.25))


if __name__ == "__main__":
    unittest.main()
