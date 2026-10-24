import random
import unittest

from maths_frenzy.core import Level, Operation, Question, QuestionGenerator


class QuestionTests(unittest.TestCase):
    def test_text_wraps_negative_right_operand(self) -> None:
        self.assertEqual(Question(5, -3, Operation.ADDITION).expression, "5 + (-3)")
        self.assertEqual(Question(-5, 3, Operation.SUBTRACTION).expression, "-5 \u2212 3")
        self.assertEqual(Question(2, 3, Operation.MULTIPLICATION).text, "What is 2 \u00d7 3?")

    def test_answers(self) -> None:
        self.assertEqual(Question(5, -3, Operation.ADDITION).answer, 2)
        self.assertEqual(Question(5, 8, Operation.SUBTRACTION).answer, -3)
        self.assertEqual(Question(-4, 6, Operation.MULTIPLICATION).answer, -24)
        self.assertEqual(Question(1, 3, Operation.DIVISION).answer, 0.33)
        self.assertEqual(Question(-2, 3, Operation.DIVISION).answer, -0.67)

    def test_is_correct_uses_two_decimal_places(self) -> None:
        question = Question(1, 3, Operation.DIVISION)
        self.assertTrue(question.is_correct(0.33))
        self.assertTrue(question.is_correct(0.333333))
        self.assertFalse(question.is_correct(0.3))
        self.assertFalse(question.is_correct(0.34))
        self.assertTrue(Question(4, 4, Operation.ADDITION).is_correct(8.0))

    def test_zero_divisor_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Question(1, 0, Operation.DIVISION)


class GeneratorTests(unittest.TestCase):
    def test_operands_stay_within_the_level_range(self) -> None:
        for level in Level:
            generator = QuestionGenerator(level, Operation.ADDITION, random.Random(1))
            for _ in range(500):
                question = generator.next_question()
                self.assertLessEqual(abs(question.left), level.max_operand)
                self.assertLessEqual(abs(question.right), level.max_operand)

    def test_division_never_divides_by_zero(self) -> None:
        generator = QuestionGenerator(Level.BEGINNER, Operation.DIVISION, random.Random(7))
        for _ in range(2000):
            self.assertNotEqual(generator.next_question().right, 0)

    def test_seeded_generators_are_reproducible(self) -> None:
        a = QuestionGenerator(Level.MASTER, Operation.MULTIPLICATION, random.Random(42))
        b = QuestionGenerator(Level.MASTER, Operation.MULTIPLICATION, random.Random(42))
        self.assertEqual([a.next_question() for _ in range(10)], [b.next_question() for _ in range(10)])

    def test_level_ranges(self) -> None:
        self.assertEqual([lvl.max_operand for lvl in Level], [20, 50, 100])


if __name__ == "__main__":
    unittest.main()
