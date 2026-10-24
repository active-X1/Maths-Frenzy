import unittest

from maths_frenzy.core import InvalidNumberError, format_number, parse_number


class ParseNumberTests(unittest.TestCase):
    def test_accepts_common_formats(self) -> None:
        cases = {"8": 8.0, " -3.5 ": -3.5, "+2": 2.0, ".5": 0.5, "1e3": 1000.0, "\u22122": -2.0}
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(parse_number(raw), expected)

    def test_rejects_bad_input(self) -> None:
        for raw in ["", "   ", "abc", "1,5", "1_000", "nan", "inf", "-inf", "1 2"]:
            with self.subTest(raw=raw), self.assertRaises(InvalidNumberError):
                parse_number(raw)


class FormatNumberTests(unittest.TestCase):
    def test_formats(self) -> None:
        cases = [(8, "8"), (8.0, "8"), (-0.0, "0"), (2.5, "2.5"), (0.1 + 0.2, "0.3"), (-0.33, "-0.33")]
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(format_number(value), expected)


if __name__ == "__main__":
    unittest.main()
