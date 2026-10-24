import unittest

from maths_frenzy.core import CalculatorError, Operation, calculate, evaluate


class EvaluateTests(unittest.TestCase):
    def test_valid_expressions(self) -> None:
        cases = {
            "1 + 2": 3,
            "2 * (3 + 4)": 14,
            "10 / 4": 2.5,
            "7 // 2": 3,
            "7 % 4": 3,
            "2 ** 10": 1024,
            "2^10": 1024,
            "-5 + 3": -2,
            "+4": 4,
            "6 \u00d7 7": 42,
            "9 \u00f7 3": 3,
            "5 \u2212 8": -3,
            "007 + 1": 8,
            "1.5 + 1.5": 3,
            ".5 + .5": 1,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate(expression), expected)

    def test_float_precision_is_left_to_the_formatter(self) -> None:
        self.assertAlmostEqual(evaluate("0.1 + 0.2"), 0.3)

    def test_division_by_zero(self) -> None:
        for expression in ["1/0", "1//0", "1%0", "0**-1"]:
            with self.subTest(expression=expression), self.assertRaisesRegex(CalculatorError, "zero"):
                evaluate(expression)

    def test_invalid_syntax(self) -> None:
        for expression in ["", "   ", "2 +", "(1", "1 2", "++", "\x00"]:
            with self.subTest(expression=expression), self.assertRaises(CalculatorError):
                evaluate(expression)

    def test_rejects_anything_that_is_not_arithmetic(self) -> None:
        dangerous = [
            "__import__('os').system('echo hi')",
            "open('x')",
            "().__class__",
            "[1, 2]",
            "'a' * 3",
            "1 if True else 2",
            "lambda: 1",
            "x + 1",
            "True + 1",
            "1 < 2",
            "1j",
        ]
        for expression in dangerous:
            with self.subTest(expression=expression), self.assertRaises(CalculatorError):
                evaluate(expression)

    def test_resource_limits(self) -> None:
        for expression in ["9**9**9", "10**100000", "(10**1000)**1000", "1e308 * 10", "x" * 500]:
            with self.subTest(expression=expression[:30]), self.assertRaises(CalculatorError):
                evaluate(expression)

    def test_complex_results_are_rejected(self) -> None:
        with self.assertRaises(CalculatorError):
            evaluate("(-8) ** 0.5")


class CalculateTests(unittest.TestCase):
    def test_each_operation(self) -> None:
        self.assertEqual(calculate(6, 3, Operation.ADDITION), 9)
        self.assertEqual(calculate(6, 3, Operation.SUBTRACTION), 3)
        self.assertEqual(calculate(6, 3, Operation.MULTIPLICATION), 18)
        self.assertEqual(calculate(6, 3, Operation.DIVISION), 2)

    def test_division_by_zero(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate(1, 0, Operation.DIVISION)

    def test_overflow(self) -> None:
        with self.assertRaises(CalculatorError):
            calculate(1e308, 10, Operation.MULTIPLICATION)


if __name__ == "__main__":
    unittest.main()
