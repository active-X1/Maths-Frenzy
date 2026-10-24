"""NiceGUI web interface.

Each browser tab gets its own :class:`WebGame`, so several people can play on the
same server at the same time without sharing any state.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable

from nicegui import ui

from maths_frenzy import __version__
from maths_frenzy.core import (
    AnswerRecord,
    CalculatorError,
    GameConfig,
    GameSession,
    InvalidNumberError,
    Level,
    Operation,
    Outcome,
    evaluate,
    format_number,
)
from maths_frenzy.core import content

__all__ = ["WebGame", "index", "run"]

KEYPAD = (
    ("C", "\u232b", "(", ")"),
    ("7", "8", "9", "\u00f7"),
    ("4", "5", "6", "\u00d7"),
    ("1", "2", "3", "\u2212"),
    ("0", ".", "=", "+"),
)
TICK_SECONDS = 0.2


class WebGame:
    """State and rendering for a single browser session."""

    def __init__(self) -> None:
        self.player = ""
        self.level = Level.BEGINNER
        self.operation = Operation.ADDITION
        self.session: GameSession | None = None
        self.deadline: float | None = None

    # ---------------------------------------------------------------- layout

    def build(self) -> None:
        """Create the page chrome. Must be called inside a ``@ui.page`` function."""
        ui.colors(primary="#6366f1", positive="#22c55e", negative="#ef4444")
        dark = ui.dark_mode()

        with ui.header(elevated=False).classes("items-center justify-between bg-primary"):
            ui.label(content.APP_NAME).classes("text-xl font-bold cursor-pointer").on(
                "click", lambda: self.show(self.menu)
            )
            ui.button(icon="contrast", on_click=dark.toggle).props("flat round color=white")

        self.body = ui.column().classes("w-full max-w-xl mx-auto items-stretch gap-4 p-4")
        ui.label(content.CREDITS).classes("text-xs text-gray-500 text-center w-full pb-4")
        ui.label(f"v{__version__}").classes("text-xs text-gray-400 text-center w-full")
        self.timer = ui.timer(TICK_SECONDS, self._tick, active=False)
        self.show(self.menu)

    def show(self, render: Callable[[], None]) -> None:
        """Swap the visible screen."""
        self.timer.active = False
        self.deadline = None
        self.body.clear()
        with self.body:
            render()

    # --------------------------------------------------------------- screens

    def menu(self) -> None:
        with ui.card().classes("w-full items-center gap-3 p-8"):
            ui.label(content.APP_NAME).classes("text-4xl font-bold")
            ui.label(content.TAGLINE).classes("text-gray-500 text-center")
            ui.button("Play", on_click=lambda: self.show(self.setup)).props(
                "unelevated size=lg"
            ).classes("w-full")
            ui.button("Calculator", on_click=lambda: self.show(self.calculator)).props(
                "outline size=lg"
            ).classes("w-full")
            ui.button("How to play", on_click=lambda: self.show(self.how_to_play)).props(
                "flat size=lg"
            ).classes("w-full")

    def how_to_play(self) -> None:
        with ui.card().classes("w-full gap-3 p-6"):
            ui.label("How to play").classes("text-2xl font-bold")
            for paragraph in content.HOW_TO_PLAY:
                ui.label(paragraph)
            ui.button("Back", on_click=lambda: self.show(self.menu)).props("flat")

    def setup(self) -> None:
        with ui.card().classes("w-full gap-3 p-6"):
            ui.label("New game").classes("text-2xl font-bold")
            name = (
                ui.input("Nickname", value=self.player, placeholder="Player")
                .props("outlined dense maxlength=20")
                .classes("w-full")
            )
            ui.label("Level").classes("text-sm font-medium")
            level = (
                ui.toggle({lvl.value: lvl.label for lvl in Level}, value=self.level.value)
                .props("spread no-caps unelevated")
                .classes("w-full")
            )
            ui.label("Operation").classes("text-sm font-medium")
            operation = (
                ui.toggle(
                    {op.value: f"{op.symbol}  {op.label}" for op in Operation},
                    value=self.operation.value,
                )
                .props("spread no-caps unelevated")
                .classes("w-full")
            )
            pledge = ui.checkbox(content.PLEDGE)

            def start() -> None:
                self.player = (name.value or "").strip() or "Player"
                self.level = Level(level.value)
                self.operation = Operation(operation.value)
                self.start_game()

            with ui.row().classes("w-full justify-between"):
                ui.button("Back", on_click=lambda: self.show(self.menu)).props("flat")
                ui.button("Start", on_click=start).props("unelevated").bind_enabled_from(
                    pledge, "value"
                )

    def game(self) -> None:
        session = self._require_session()
        timed = session.config.seconds_per_question is not None
        with ui.card().classes("w-full gap-2 p-6"):
            with ui.row().classes("w-full justify-between"):
                self.progress_label = ui.label().classes("text-sm text-gray-500")
                self.score_label = ui.label().classes("text-sm text-gray-500")
            if timed:
                self.time_bar = ui.linear_progress(value=1.0, show_value=False).props(
                    "rounded size=10px"
                )
                self.time_label = ui.label().classes("self-end text-sm text-gray-500")
            self.question_label = ui.label().classes("text-4xl font-bold text-center w-full py-4")
            self.answer = (
                ui.input("Your answer")
                .props("outlined autofocus")
                .classes("w-full text-xl")
            )
            self.answer.on("keydown.enter", self.submit)
            self.feedback = ui.label("\u00a0").classes("text-center w-full min-h-6")
            with ui.row().classes("w-full justify-between"):
                ui.button("Submit", on_click=self.submit).props("unelevated")
                ui.button("Calculator", on_click=self._calculator_dialog).props("outline")
                ui.button(
                    "Quit",
                    on_click=lambda: self._confirm("Leave this game?", lambda: self.show(self.menu)),
                ).props("flat color=negative")
        self._load_question(focus=False)

    def results(self) -> None:
        session = self._require_session()
        result = session.result()
        with ui.card().classes("w-full items-center gap-2 p-8"):
            ui.label(f"Game over, {session.player}!").classes("text-2xl font-bold")
            ui.label(f"{result.score} / {result.total}").classes("text-6xl font-bold text-primary")
            ui.label(f"{result.accuracy:.0%} accuracy \u2022 {result.rank}").classes("text-gray-500")
            mistakes = result.mistakes
            if mistakes:
                ui.separator()
                ui.label("Review").classes("font-medium")
                for record in mistakes[:5]:
                    mine = "no answer" if record.given is None else format_number(record.given)
                    answer = format_number(record.question.answer)
                    ui.label(f"{record.question.expression} = {answer}  (you: {mine})").classes(
                        "text-sm text-gray-500"
                    )
                if len(mistakes) > 5:
                    ui.label(f"\u2026and {len(mistakes) - 5} more").classes("text-sm text-gray-500")
            with ui.row().classes("pt-4 gap-2"):
                ui.button("Play again", on_click=self.start_game).props("unelevated")
                ui.button("Main menu", on_click=lambda: self.show(self.menu)).props("outline")

    def calculator(self) -> None:
        with ui.card().classes("w-full gap-3 p-6"):
            ui.label("Calculator").classes("text-2xl font-bold")
            self._calculator_widget()
            ui.button("Back", on_click=lambda: self.show(self.menu)).props("flat")

    # ------------------------------------------------------------- game flow

    def start_game(self) -> None:
        config = GameConfig(self.level, self.operation)
        self.session = GameSession(config, player=self.player)
        self.show(self.game)

    def submit(self, _event: object = None) -> None:
        session = self.session
        if session is None or session.finished:
            return
        try:
            record = session.submit(self.answer.value or "")
        except InvalidNumberError as exc:
            ui.notify(str(exc), type="warning")
            return
        self._after_answer(record)

    def _after_answer(self, record: AnswerRecord) -> None:
        session = self._require_session()
        if session.finished:
            self.show(self.results)
            return
        answer = format_number(record.question.answer)
        if record.outcome is Outcome.CORRECT:
            self.feedback.text = "Correct!"
            self.feedback.classes(replace="text-center w-full min-h-6 text-positive")
        elif record.outcome is Outcome.TIMEOUT:
            self.feedback.text = f"Time's up! It was {answer}."
            self.feedback.classes(replace="text-center w-full min-h-6 text-negative")
        else:
            self.feedback.text = f"Sorry, the answer was {answer}."
            self.feedback.classes(replace="text-center w-full min-h-6 text-negative")
        self._load_question(focus=True)

    def _load_question(self, *, focus: bool) -> None:
        session = self._require_session()
        question = session.current
        assert question is not None
        self.progress_label.text = f"Question {session.number} of {session.config.question_count}"
        self.score_label.text = f"Score: {session.score}"
        self.question_label.text = question.expression + " = ?"
        self.answer.value = ""
        if focus:
            self.answer.run_method("focus")
        limit = session.config.seconds_per_question
        if limit is not None:
            self.deadline = time.monotonic() + limit
            self.time_bar.value = 1.0
            self.time_label.text = f"{limit}s"
            self.timer.active = True

    def _tick(self) -> None:
        session = self.session
        if session is None or session.finished or self.deadline is None:
            return
        limit = session.config.seconds_per_question
        assert limit is not None
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            self._after_answer(session.time_out())
            return
        self.time_bar.value = remaining / limit
        self.time_label.text = f"{math.ceil(remaining)}s"

    # ---------------------------------------------------------------- helpers

    def _require_session(self) -> GameSession:
        if self.session is None:
            raise RuntimeError("No game in progress.")
        return self.session

    def _confirm(self, message: str, on_yes: Callable[[], None]) -> None:
        with ui.dialog() as dialog, ui.card():
            ui.label(message)
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=dialog.close).props("flat")

                def confirmed() -> None:
                    dialog.close()
                    on_yes()

                ui.button("Yes", on_click=confirmed).props("unelevated")
        dialog.open()

    def _calculator_dialog(self) -> None:
        with ui.dialog() as dialog, ui.card().classes("gap-3"):
            self._calculator_widget()
            ui.button("Close", on_click=dialog.close).props("flat")
        dialog.open()

    @staticmethod
    def _calculator_widget() -> None:
        display = (
            ui.input(placeholder="0")
            .props("outlined input-class=text-right")
            .classes("w-full text-xl")
        )
        message = ui.label("\u00a0").classes("text-negative text-sm min-h-5")

        def press(key: str) -> None:
            message.text = "\u00a0"
            current = display.value or ""
            if key == "C":
                display.value = ""
            elif key == "\u232b":
                display.value = current[:-1]
            elif key == "=":
                try:
                    display.value = format_number(evaluate(current))
                except CalculatorError as exc:
                    message.text = str(exc)
            else:
                display.value = current + key

        display.on("keydown.enter", lambda: press("="))
        with ui.grid(columns=4).classes("w-full gap-2"):
            for row in KEYPAD:
                for key in row:
                    colour = "primary" if key == "=" else "grey-8"
                    ui.button(key, on_click=lambda k=key: press(k)).props(
                        f"unelevated color={colour}"
                    ).classes("text-lg")


@ui.page("/")
def index() -> None:
    WebGame().build()


def run(
    *,
    host: str = "127.0.0.1",
    port: int = 8080,
    show: bool = True,
    reload: bool = False,
) -> None:
    """Start the NiceGUI server (blocks until it is stopped)."""
    ui.run(
        title=content.APP_NAME,
        host=host,
        port=port,
        show=show,
        reload=reload,
        favicon="\U0001f9ee",
    )
