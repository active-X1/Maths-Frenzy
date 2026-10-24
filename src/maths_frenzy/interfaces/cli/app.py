"""Interactive and scriptable terminal interface."""

from __future__ import annotations

import argparse
import random
import textwrap
import time
from collections.abc import Callable, Sequence
from typing import TypeVar

from maths_frenzy import __version__
from maths_frenzy.core import (
    AnswerRecord,
    CalculatorError,
    GameConfig,
    GameResult,
    GameSession,
    InvalidNumberError,
    Level,
    Operation,
    Outcome,
    evaluate,
    format_number,
)
from maths_frenzy.core.content import APP_NAME, CREDITS, HOW_TO_PLAY, PLEDGE, TAGLINE
from maths_frenzy.core.session import DEFAULT_QUESTION_COUNT, DEFAULT_SECONDS_PER_QUESTION

from .console import BOLD, CYAN, DIM, GREEN, RED, YELLOW, Console

__all__ = ["CliApp", "build_parser", "main"]

T = TypeVar("T")

_QUIT_WORDS = {"q", "quit", "exit"}
_YES_WORDS = {"y", "yes"}
_WIDTH = 64


def _level_label(level: Level) -> str:
    return f"{level.label}  ({level.description})"


def _operation_label(operation: Operation) -> str:
    return f"{operation.label}  ({operation.symbol})"


class CliApp:
    """Terminal front-end. All output goes through the injected :class:`Console`."""

    def __init__(self, console: Console | None = None, rng: random.Random | None = None) -> None:
        self.console = console if console is not None else Console()
        self._rng = rng
        self.session: GameSession | None = None

    # ------------------------------------------------------------------ menus

    def run_menu(self) -> int:
        """Interactive main menu."""
        self._banner()
        agreed = False
        while True:
            choice = self._choose(
                "Main menu", ["Play the game", "Calculator", "How to play", "Quit"]
            )
            if choice is None or choice == 3:
                self.console.print(self.console.style("Goodbye!", CYAN))
                return 0
            if choice == 0:
                agreed = agreed or self._pledge()
                if agreed:
                    self._play_interactive()
            elif choice == 1:
                self.calculator()
            else:
                self.how_to_play()

    def _play_interactive(self) -> None:
        while True:
            config = self.choose_config()
            if config is None:
                return
            name = self.console.ask(self.console.style("Your nickname", BOLD) + " [Player]: ")
            self.play(config, (name or "").strip() or "Player")
            again = self.console.ask("Play again? [y/N]: ")
            if (again or "").strip().lower() not in _YES_WORDS:
                return

    def choose_config(
        self,
        level: Level | None = None,
        operation: Operation | None = None,
        *,
        question_count: int = DEFAULT_QUESTION_COUNT,
        seconds_per_question: int | None = DEFAULT_SECONDS_PER_QUESTION,
    ) -> GameConfig | None:
        """Ask for whichever of level/operation is missing and build a config."""
        level = level or self._choose_one("Choose a level", list(Level), _level_label)
        if level is None:
            return None
        operation = operation or self._choose_one(
            "Choose an operation", list(Operation), _operation_label
        )
        if operation is None:
            return None
        return GameConfig(level, operation, question_count, seconds_per_question)

    def _pledge(self) -> bool:
        self.console.print()
        self.console.print(self.console.style(f'  "{PLEDGE}"', YELLOW))
        answer = self.console.ask("  Do you agree? [y/N]: ")
        agreed = (answer or "").strip().lower() in _YES_WORDS
        if not agreed:
            self.console.print(
                self.console.style("  You need to agree to play. Back to the menu.", DIM)
            )
        return agreed

    # ------------------------------------------------------------------- game

    def play(self, config: GameConfig, player: str = "Player") -> GameResult | None:
        """Play one round. Returns ``None`` if the player quits early."""
        console = self.console
        session = GameSession(config, player=player, rng=self._rng)
        self.session = session
        limit = config.seconds_per_question
        timer_note = f"{limit}s per question" if limit else "no timer"
        console.print()
        console.print(
            console.style(
                f"{config.level.label} {config.operation.label}  |  "
                f"{config.question_count} questions  |  {timer_note}",
                BOLD,
            )
        )
        console.print(console.style("Type q to quit. Division answers use 2 decimal places.", DIM))
        console.print()
        while (question := session.current) is not None:
            record = self._ask_question(session, question.text)
            if record is None:
                console.print(console.style("Game abandoned.", DIM))
                return None
            self._feedback(record)
        result = session.result()
        self._show_result(player, result)
        return result

    def _ask_question(self, session: GameSession, text: str) -> AnswerRecord | None:
        limit = session.config.seconds_per_question
        deadline = time.monotonic() + limit if limit else None
        prompt = (
            self.console.style(f"[{session.number}/{session.config.question_count}] ", DIM)
            + self.console.style(text, BOLD)
            + (self.console.style(f"  ({limit}s)", DIM) if limit else "")
            + " > "
        )
        while True:
            remaining = None if deadline is None else deadline - time.monotonic()
            if remaining is not None and remaining <= 0:
                return session.time_out()
            raw = self.console.ask(prompt, remaining)
            if raw is None:
                return session.time_out()
            if raw.strip().lower() in _QUIT_WORDS:
                return None
            try:
                return session.submit(raw)
            except InvalidNumberError as exc:
                self.console.print(self.console.style(f"  {exc}", YELLOW))

    def _feedback(self, record: AnswerRecord) -> None:
        console = self.console
        answer = format_number(record.question.answer)
        if record.outcome is Outcome.CORRECT:
            console.print(console.style("  Correct!", GREEN))
        elif record.outcome is Outcome.TIMEOUT:
            console.print(console.style(f"  Time's up! The answer was {answer}.", RED))
        else:
            console.print(console.style(f"  Sorry, the answer was {answer}.", RED))

    def _show_result(self, player: str, result: GameResult) -> None:
        console = self.console
        console.print()
        console.print(console.style(f" Results for {player} ".center(_WIDTH, "-"), BOLD, CYAN))
        console.print(f"  Score:  {result.score} / {result.total}  ({result.accuracy:.0%})")
        console.print(f"  Rank:   {console.style(result.rank, BOLD, YELLOW)}")
        mistakes = result.mistakes
        if mistakes:
            console.print()
            console.print(console.style("  Review", BOLD))
            for record in mistakes[:5]:
                mine = "no answer" if record.given is None else format_number(record.given)
                console.print(
                    f"   {record.question.expression} = {format_number(record.question.answer)}"
                    + console.style(f"   (you: {mine})", DIM)
                )
            if len(mistakes) > 5:
                console.print(console.style(f"   ...and {len(mistakes) - 5} more", DIM))
        console.print("-" * _WIDTH)

    # ------------------------------------------------------------- calculator

    def calculator(self, expression: str | None = None) -> int:
        """Evaluate ``expression`` once, or open a calculator prompt if it is ``None``."""
        console = self.console
        if expression is not None:
            try:
                console.print(format_number(evaluate(expression)))
            except CalculatorError as exc:
                console.print(console.style(f"Error: {exc}", RED))
                return 1
            return 0
        console.print(console.style("Calculator", BOLD, CYAN))
        console.print(
            console.style("Try 2*(3+4), 10/4 or 2^8. Press Enter or type q to go back.", DIM)
        )
        while True:
            raw = console.ask(console.style("calc> ", CYAN))
            if raw is None or not raw.strip() or raw.strip().lower() in _QUIT_WORDS:
                return 0
            try:
                console.print("  = " + console.style(format_number(evaluate(raw)), BOLD))
            except CalculatorError as exc:
                console.print(console.style(f"  {exc}", YELLOW))

    # ------------------------------------------------------------------- misc

    def how_to_play(self) -> None:
        self.console.print()
        self.console.print(self.console.style("How to play", BOLD, CYAN))
        for paragraph in HOW_TO_PLAY:
            self.console.print(
                textwrap.fill(paragraph, _WIDTH, initial_indent="  ", subsequent_indent="  ")
            )
            self.console.print()

    def _banner(self) -> None:
        title = f"{APP_NAME.upper()}  v{__version__}"
        inner = max(len(title), len(TAGLINE)) + 4
        console = self.console
        console.print()
        console.print(console.style("+" + "-" * inner + "+", CYAN))
        console.print(console.style("|" + title.center(inner) + "|", BOLD, CYAN))
        console.print(console.style("|" + TAGLINE.center(inner) + "|", CYAN))
        console.print(console.style("+" + "-" * inner + "+", CYAN))
        console.print(console.style(CREDITS, DIM))

    def _choose(self, title: str, options: Sequence[str]) -> int | None:
        """Show a numbered menu. Returns the 0-based choice, or ``None`` for q."""
        console = self.console
        console.print()
        console.print(console.style(title, BOLD))
        for number, option in enumerate(options, start=1):
            console.print(f"  {console.style(str(number), CYAN)}) {option}")
        while True:
            raw = (console.ask(f"Choose 1-{len(options)} (q to go back): ") or "").strip().lower()
            if raw in _QUIT_WORDS:
                return None
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return int(raw) - 1
            console.print(console.style("  Please pick one of the numbers above.", YELLOW))

    def _choose_one(
        self, title: str, members: Sequence[T], label: Callable[[T], str]
    ) -> T | None:
        index = self._choose(title, [label(member) for member in members])
        return None if index is None else members[index]


# ------------------------------------------------------------------- argparse


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number") from None
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maths-frenzy cli",
        description=f"{APP_NAME}: {TAGLINE} (terminal edition)",
        epilog="With no command, the interactive menu starts.",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--no-color", action="store_true", help="disable coloured output")
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")

    commands.add_parser("menu", help="start the interactive menu (default)")

    play = commands.add_parser("play", help="play a round straight away")
    play.add_argument("-l", "--level", choices=[x.value for x in Level], help="difficulty level")
    play.add_argument(
        "-o", "--operation", choices=[x.value for x in Operation], help="arithmetic operation"
    )
    play.add_argument(
        "-n",
        "--questions",
        type=_positive_int,
        default=DEFAULT_QUESTION_COUNT,
        metavar="N",
        help="number of questions (default: %(default)s)",
    )
    play.add_argument(
        "-t",
        "--time",
        type=_positive_int,
        default=DEFAULT_SECONDS_PER_QUESTION,
        metavar="SECONDS",
        help="seconds per question (default: %(default)s)",
    )
    play.add_argument("--no-timer", action="store_true", help="practice mode without a timer")
    play.add_argument("-p", "--player", default="Player", help="your nickname")

    calc = commands.add_parser("calc", help="evaluate an expression, or open a calculator prompt")
    calc.add_argument(
        "expression", nargs="*", help='e.g. "2*(3+4)"; put -- before expressions starting with -'
    )

    commands.add_parser("howto", help="show the rules")
    return parser


def main(argv: Sequence[str] | None = None, *, console: Console | None = None) -> int:
    """Entry point for ``maths-frenzy cli``."""
    args = build_parser().parse_args(argv)
    console = console if console is not None else Console(color=False if args.no_color else None)
    app = CliApp(console)
    command = args.command or "menu"
    try:
        if command == "play":
            return _run_play(app, args)
        if command == "calc":
            expression = " ".join(args.expression).strip()
            return app.calculator(expression or None)
        if command == "howto":
            app.how_to_play()
            return 0
        return app.run_menu()
    except KeyboardInterrupt:
        console.print()
        console.print("Interrupted.")
        return 130
    except EOFError:
        console.print()
        return 0


def _run_play(app: CliApp, args: argparse.Namespace) -> int:
    config = app.choose_config(
        Level(args.level) if args.level else None,
        Operation(args.operation) if args.operation else None,
        question_count=args.questions,
        seconds_per_question=None if args.no_timer else args.time,
    )
    if config is not None:
        app.play(config, args.player)
    return 0
