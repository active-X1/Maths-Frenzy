import io
import random
import unittest
from collections.abc import Callable
from contextlib import redirect_stderr, redirect_stdout

from maths_frenzy.core import GameConfig, Level, Operation, format_number
from maths_frenzy.interfaces.cli import CliApp, main
from maths_frenzy.interfaces.cli.console import Console


class ScriptedConsole(Console):
    """A console that never touches the real terminal."""

    def __init__(self, replies: Callable[[str, "ScriptedConsole"], str | None]) -> None:
        super().__init__(color=False)
        self.replies = replies
        self.output: list[str] = []
        self.prompts: list[str] = []
        self.app: CliApp | None = None

    def print(self, text: str = "", *, end: str = "\n") -> None:
        self.output.append(text)

    def ask(self, prompt: str, timeout: float | None = None) -> str | None:
        self.prompts.append(prompt)
        reply = self.replies(prompt, self)
        if reply is None and timeout is None:
            raise EOFError
        return reply

    @property
    def text(self) -> str:
        return "\n".join(self.output)


def correct_answer(console: ScriptedConsole) -> str:
    assert console.app is not None and console.app.session is not None
    question = console.app.session.current
    assert question is not None
    return format_number(question.answer)


def make_app(replies: Callable[[str, ScriptedConsole], str | None]) -> tuple[CliApp, ScriptedConsole]:
    console = ScriptedConsole(replies)
    app = CliApp(console, rng=random.Random(5))
    console.app = app
    return app, console


class PlayTests(unittest.TestCase):
    config = GameConfig(Level.BEGINNER, Operation.ADDITION, question_count=3, seconds_per_question=5)

    def test_perfect_round(self) -> None:
        app, console = make_app(lambda prompt, c: correct_answer(c))
        result = app.play(self.config, "Ada")
        assert result is not None
        self.assertEqual(result.score, 3)
        self.assertIn("Score:  3 / 3", console.text)
        self.assertIn("Maths Wizard", console.text)
        self.assertEqual(console.text.count("Correct!"), 3)

    def test_invalid_then_valid_answer(self) -> None:
        replies = iter(["abc", None])

        def reply(prompt: str, c: ScriptedConsole) -> str | None:
            first = next(replies, "x")
            return first if first != "x" else correct_answer(c)

        app, console = make_app(reply)
        app.play(GameConfig(Level.BEGINNER, Operation.ADDITION, question_count=1), "Ada")
        self.assertIn("not a valid number", console.text)

    def test_timeouts_are_reported_with_the_answer(self) -> None:
        app, console = make_app(lambda prompt, c: None)  # timer expires every time
        result = app.play(self.config, "Ada")
        assert result is not None
        self.assertEqual(result.score, 0)
        self.assertEqual(console.text.count("Time's up!"), 3)
        self.assertIn("(you: no answer)", console.text)

    def test_quitting_abandons_the_game(self) -> None:
        app, console = make_app(lambda prompt, c: "q")
        self.assertIsNone(app.play(self.config, "Ada"))
        self.assertIn("Game abandoned", console.text)

    def test_untimed_mode_hides_the_timer(self) -> None:
        app, console = make_app(lambda prompt, c: correct_answer(c))
        app.play(GameConfig(Level.BEGINNER, Operation.ADDITION, 2, None), "Ada")
        self.assertIn("no timer", console.text)
        self.assertFalse(any("s)" in prompt for prompt in console.prompts))


class CalculatorTests(unittest.TestCase):
    def test_one_shot(self) -> None:
        app, console = make_app(lambda prompt, c: None)
        self.assertEqual(app.calculator("2*(3+4)"), 0)
        self.assertEqual(console.text, "14")

    def test_one_shot_error(self) -> None:
        app, console = make_app(lambda prompt, c: None)
        self.assertEqual(app.calculator("1/0"), 1)
        self.assertIn("Cannot divide by zero", console.text)

    def test_prompt_loop(self) -> None:
        replies = iter(["1+1", "oops(", ""])
        app, console = make_app(lambda prompt, c: next(replies))
        self.assertEqual(app.calculator(), 0)
        self.assertIn("= 2", console.text)
        self.assertIn("Invalid expression", console.text)


class MenuTests(unittest.TestCase):
    def test_full_menu_session(self) -> None:
        script = iter(["3", "2", "2+2", "", "1", "y", "1", "2", "Ada", "q", "n", "4"])
        app, console = make_app(lambda prompt, c: next(script))
        self.assertEqual(app.run_menu(), 0)
        for expected in ["MATHS FRENZY", "How to play", "= 4", "Beginner Subtraction", "Goodbye!"]:
            self.assertIn(expected, console.text)

    def test_declining_the_pledge_returns_to_the_menu(self) -> None:
        script = iter(["1", "n", "4"])
        app, console = make_app(lambda prompt, c: next(script))
        app.run_menu()
        self.assertIn("You need to agree", console.text)
        self.assertNotIn("Choose a level", console.text)

    def test_bad_menu_input_reprompts(self) -> None:
        script = iter(["9", "zzz", "4"])
        app, console = make_app(lambda prompt, c: next(script))
        app.run_menu()
        self.assertEqual(console.text.count("Please pick one of the numbers"), 2)


class MainTests(unittest.TestCase):
    def run_main(self, *argv: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--no-color", *argv])
        return code, buffer.getvalue()

    def test_calc_command(self) -> None:
        self.assertEqual(self.run_main("calc", "2", "+", "2"), (0, "4\n"))

    def test_calc_error_exit_code(self) -> None:
        code, output = self.run_main("calc", "1/0")
        self.assertEqual(code, 1)
        self.assertIn("Cannot divide by zero", output)

    def test_howto_command(self) -> None:
        code, output = self.run_main("howto")
        self.assertEqual(code, 0)
        self.assertIn("three levels", output)

    def test_play_rejects_bad_arguments(self) -> None:
        for argv in (["play", "--level", "impossible"], ["play", "-n", "0"], ["play", "-t", "x"]):
            with (
                self.subTest(argv=argv),
                redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as ctx,
            ):
                main(argv)
            self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
