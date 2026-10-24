"""Every screen of the desktop interface. Each screen is a ``ttk.Frame``."""

from __future__ import annotations

import math
import time
import tkinter as tk
from collections.abc import Callable
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING

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
    calculate,
    format_number,
    parse_number,
)
from maths_frenzy.core import content

from .keypad import KeypadCalculator, open_calculator_window
from .theme import FONT_FAMILY

if TYPE_CHECKING:
    from .app import MathsFrenzyApp

__all__ = [
    "CalculatorMenu",
    "GameScreen",
    "HelpScreen",
    "KeypadScreen",
    "MainMenu",
    "PledgeScreen",
    "ResultsScreen",
    "Screen",
    "SetupScreen",
    "TutorialScreen",
    "TwoNumberScreen",
]

BUTTON_WIDTH = 26
TICK_MS = 100


class Screen(ttk.Frame):
    """Base class: a full-window page that can navigate via ``self.app.show``."""

    def __init__(self, parent: tk.Misc, app: MathsFrenzyApp) -> None:
        super().__init__(parent, style="App.TFrame", padding=24)
        self.app = app
        self.build()

    def build(self) -> None:
        raise NotImplementedError

    def on_leave(self) -> None:
        """Called just before the screen is destroyed. Cancel timers here."""

    def destroy(self) -> None:
        self.on_leave()
        super().destroy()

    # -- small widget helpers -------------------------------------------------

    def centered(self) -> ttk.Frame:
        box = ttk.Frame(self, style="App.TFrame")
        box.pack(expand=True)
        return box

    @staticmethod
    def label(parent: tk.Misc, text: str, style: str = "Body.TLabel", **pack: object) -> ttk.Label:
        widget = ttk.Label(parent, text=text, style=style, justify="center")
        widget.pack(**pack)  # type: ignore[arg-type]
        return widget

    @staticmethod
    def button(
        parent: tk.Misc,
        text: str,
        command: Callable[[], object],
        style: str = "Primary.TButton",
        width: int = BUTTON_WIDTH,
    ) -> ttk.Button:
        widget = ttk.Button(parent, text=text, command=command, style=style, width=width)
        widget.configure(cursor="hand2")
        widget.pack(pady=5)
        return widget


# ------------------------------------------------------------------------ menus


class MainMenu(Screen):
    def build(self) -> None:
        self.label(self, content.CREDITS, "Muted.TLabel", side="bottom")
        box = self.centered()
        self.label(box, content.APP_NAME.upper(), "Title.TLabel")
        self.label(box, content.TAGLINE, "Muted.TLabel", pady=(4, 28))
        self.button(box, "Play the game", lambda: self.app.show(PledgeScreen))
        self.button(box, "Calculator", lambda: self.app.show(CalculatorMenu), "Secondary.TButton")
        self.button(box, "How to play", lambda: self.app.show(HelpScreen), "Secondary.TButton")
        self.button(box, "Exit", self.app.confirm_exit, "Danger.TButton")


class HelpScreen(Screen):
    def build(self) -> None:
        box = self.centered()
        self.label(box, "How to play", "Heading.TLabel", pady=(0, 16))
        for paragraph in content.HOW_TO_PLAY:
            ttk.Label(box, text=paragraph, style="Body.TLabel", wraplength=520).pack(pady=6)
        self.button(box, "Try the tutorial", lambda: self.app.show(TutorialScreen))
        self.button(box, "Back", lambda: self.app.show(MainMenu), "Secondary.TButton")


class TutorialScreen(Screen):
    def build(self) -> None:
        box = self.centered()
        self.label(box, content.TUTORIAL_INTRO, "Muted.TLabel")
        self.label(box, f"{content.TUTORIAL_QUESTION} = ?", "Question.TLabel", pady=20)
        self.entry = ttk.Entry(box, justify="center", font=(FONT_FAMILY, 16))
        self.entry.pack(pady=6)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda _event: self.check())
        self.message = self.label(box, content.TUTORIAL_HINT, "Muted.TLabel", pady=8)
        self.action = self.button(box, "Check", self.check)
        self.button(box, "Back", lambda: self.app.show(HelpScreen), "Secondary.TButton")

    def check(self) -> None:
        try:
            value = parse_number(self.entry.get())
        except InvalidNumberError as exc:
            self.message.configure(text=str(exc), style="Warning.TLabel")
            return
        if value == content.TUTORIAL_ANSWER:
            self.message.configure(text=content.TUTORIAL_DONE, style="Success.TLabel")
            self.action.configure(text="Start playing", command=lambda: self.app.show(SetupScreen))
        else:
            self.message.configure(text=content.TUTORIAL_HINT, style="Warning.TLabel")


class PledgeScreen(Screen):
    def build(self) -> None:
        box = self.centered()
        self.label(box, "Before we start...", "Heading.TLabel", pady=(0, 12))
        self.label(box, f"\u201c{content.PLEDGE}\u201d", "Body.TLabel", pady=10)
        self.message = self.label(box, "", "Warning.TLabel", pady=6)
        self.button(box, "I agree", lambda: self.app.show(SetupScreen))
        self.button(box, "No, I don't", self.refuse, "Secondary.TButton")
        self.button(box, "Back", lambda: self.app.show(MainMenu), "Secondary.TButton")

    def refuse(self) -> None:
        self.message.configure(text=content.PLEDGE_REQUIRED)


# ------------------------------------------------------------------ calculators


class CalculatorMenu(Screen):
    def build(self) -> None:
        box = self.centered()
        self.label(box, "Calculator", "Heading.TLabel", pady=(0, 16))
        self.button(box, "Two-number calculator", lambda: self.app.show(TwoNumberScreen))
        self.button(box, "Keypad calculator", lambda: self.app.show(KeypadScreen))
        self.button(box, "Back", lambda: self.app.show(MainMenu), "Secondary.TButton")


class KeypadScreen(Screen):
    def build(self) -> None:
        box = self.centered()
        KeypadCalculator(box).pack()
        self.button(box, "Back", lambda: self.app.show(CalculatorMenu), "Secondary.TButton")


class TwoNumberScreen(Screen):
    OPERATIONS = list(Operation)

    def build(self) -> None:
        box = self.centered()
        self.label(box, "Two-number calculator", "Heading.TLabel", pady=(0, 16))
        row = ttk.Frame(box, style="App.TFrame")
        row.pack(pady=6)
        self.left = ttk.Entry(row, width=12, justify="center", font=(FONT_FAMILY, 14))
        self.left.grid(row=0, column=0, padx=6)
        self.operation = ttk.Combobox(
            row,
            state="readonly",
            width=3,
            justify="center",
            values=[op.symbol for op in self.OPERATIONS],
            font=(FONT_FAMILY, 14),
        )
        self.operation.current(0)
        self.operation.grid(row=0, column=1, padx=6)
        self.right = ttk.Entry(row, width=12, justify="center", font=(FONT_FAMILY, 14))
        self.right.grid(row=0, column=2, padx=6)
        self.left.focus_set()
        for entry in (self.left, self.right):
            entry.bind("<Return>", lambda _event: self.calculate())
        self.result = self.label(box, "", "Body.TLabel", pady=14)
        self.button(box, "Calculate", self.calculate)
        self.button(box, "Back", lambda: self.app.show(CalculatorMenu), "Secondary.TButton")

    def calculate(self) -> None:
        operation = self.OPERATIONS[self.operation.current()]
        try:
            left = parse_number(self.left.get())
            right = parse_number(self.right.get())
            answer = calculate(left, right, operation)
        except (InvalidNumberError, CalculatorError) as exc:
            self.result.configure(text=str(exc), style="Warning.TLabel")
            return
        text = f"{format_number(left)} {operation.symbol} {format_number(right)} = "
        self.result.configure(text=text + format_number(answer), style="Success.TLabel")


# ------------------------------------------------------------------------- game


class SetupScreen(Screen):
    def build(self) -> None:
        box = self.centered()
        self.label(box, "New game", "Heading.TLabel", pady=(0, 14))

        self.label(box, "Nickname", "Muted.TLabel")
        self.name = tk.StringVar(value=self.app.player)
        entry = ttk.Entry(box, textvariable=self.name, width=24, justify="center")
        entry.pack(pady=(2, 12))
        entry.focus_set()

        self.level = tk.StringVar(value=self.app.level.value)
        self.label(box, "Level", "Muted.TLabel")
        for level in Level:
            ttk.Radiobutton(
                box, text=f"{level.label}  ({level.description})", value=level.value,
                variable=self.level,
            ).pack(anchor="w", pady=2)

        self.operation = tk.StringVar(value=self.app.operation.value)
        self.label(box, "Operation", "Muted.TLabel", pady=(12, 0))
        for operation in Operation:
            ttk.Radiobutton(
                box, text=f"{operation.label}  ({operation.symbol})", value=operation.value,
                variable=self.operation,
            ).pack(anchor="w", pady=2)

        self.button(box, "Start", self.start).pack_configure(pady=(18, 5))
        self.button(box, "Back", lambda: self.app.show(MainMenu), "Secondary.TButton")

    def start(self) -> None:
        self.app.player = self.name.get().strip() or "Player"
        self.app.level = Level(self.level.get())
        self.app.operation = Operation(self.operation.get())
        session = GameSession(GameConfig(self.app.level, self.app.operation), player=self.app.player)
        self.app.show(GameScreen, session=session)


class GameScreen(Screen):
    def __init__(self, parent: tk.Misc, app: MathsFrenzyApp, session: GameSession) -> None:
        self.session = session
        self._after_id: str | None = None
        self._deadline = 0.0
        self._calculator: tk.Toplevel | None = None
        super().__init__(parent, app)

    def build(self) -> None:
        limit = self.session.config.seconds_per_question

        top = ttk.Frame(self, style="App.TFrame")
        top.pack(fill="x")
        self.progress_label = ttk.Label(top, style="Muted.TLabel")
        self.progress_label.pack(side="left")
        self.score_label = ttk.Label(top, style="Muted.TLabel")
        self.score_label.pack(side="right")

        self.time_bar: ttk.Progressbar | None = None
        self.time_label: ttk.Label | None = None
        if limit is not None:
            self.time_bar = ttk.Progressbar(
                self, style="Timer.Horizontal.TProgressbar", maximum=1.0, value=1.0
            )
            self.time_bar.pack(fill="x", pady=(14, 2))
            self.time_label = ttk.Label(self, style="Muted.TLabel")
            self.time_label.pack(anchor="e")

        box = self.centered()
        self.question_label = self.label(box, "", "Question.TLabel", pady=(10, 16))
        self.entry = ttk.Entry(box, justify="center", font=(FONT_FAMILY, 18), width=14)
        self.entry.pack(pady=6)
        self.entry.bind("<Return>", lambda _event: self.submit())
        self.feedback = self.label(box, " ", "Muted.TLabel", pady=8)
        self.button(box, "Submit", self.submit)
        self.button(box, "Calculator", self.open_calculator, "Secondary.TButton")
        self.button(box, "Quit game", self.quit_game, "Danger.TButton")
        self.show_question()

    # -- flow -----------------------------------------------------------------

    def show_question(self) -> None:
        session, question = self.session, self.session.current
        assert question is not None
        self.progress_label.configure(
            text=f"Question {session.number} of {session.config.question_count}"
        )
        self.score_label.configure(text=f"Score: {session.score}")
        self.question_label.configure(text=question.expression + " = ?")
        self.entry.delete(0, tk.END)
        self.entry.focus_set()
        self._cancel_tick()
        limit = session.config.seconds_per_question
        if limit is not None:
            self._deadline = time.monotonic() + limit
            self.tick()

    def submit(self) -> None:
        try:
            record = self.session.submit(self.entry.get())
        except InvalidNumberError as exc:
            self.feedback.configure(text=str(exc), style="Warning.TLabel")
            return
        self.advance(record)

    def tick(self) -> None:
        limit = self.session.config.seconds_per_question
        assert limit is not None and self.time_bar is not None and self.time_label is not None
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            self.advance(self.session.time_out())
            return
        self.time_bar.configure(value=remaining / limit)
        self.time_label.configure(text=f"{math.ceil(remaining)}s")
        self._after_id = self.after(TICK_MS, self.tick)

    def advance(self, record: AnswerRecord) -> None:
        self._cancel_tick()
        if self.session.finished:
            self.app.show(ResultsScreen, result=self.session.result())
            return
        answer = format_number(record.question.answer)
        if record.outcome is Outcome.CORRECT:
            self.feedback.configure(text="Correct!", style="Success.TLabel")
        elif record.outcome is Outcome.TIMEOUT:
            self.feedback.configure(text=f"Time's up! It was {answer}.", style="Danger.TLabel")
        else:
            self.feedback.configure(text=f"Sorry, the answer was {answer}.", style="Danger.TLabel")
        self.show_question()

    def quit_game(self) -> None:
        if messagebox.askyesno("Quit game", "Leave this game? Your progress will be lost."):
            self.app.show(MainMenu)

    def open_calculator(self) -> None:
        if self._calculator is not None and self._calculator.winfo_exists():
            self._calculator.lift()
            return
        self._calculator = open_calculator_window(self.app)

    def _cancel_tick(self) -> None:
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def on_leave(self) -> None:
        self._cancel_tick()
        if self._calculator is not None and self._calculator.winfo_exists():
            self._calculator.destroy()


class ResultsScreen(Screen):
    def __init__(self, parent: tk.Misc, app: MathsFrenzyApp, result: GameResult) -> None:
        self.result = result
        super().__init__(parent, app)

    def build(self) -> None:
        result = self.result
        box = self.centered()
        self.label(box, f"Game over, {self.app.player}!", "Heading.TLabel")
        self.label(box, f"{result.score} / {result.total}", "Score.TLabel", pady=(10, 0))
        self.label(box, f"{result.accuracy:.0%} accuracy  \u2022  {result.rank}", "Muted.TLabel")

        mistakes = result.mistakes
        if mistakes:
            self.label(box, "Review", "Body.TLabel", pady=(16, 4))
            for record in mistakes[:5]:
                mine = "no answer" if record.given is None else format_number(record.given)
                text = (
                    f"{record.question.expression} = {format_number(record.question.answer)}"
                    f"   (you: {mine})"
                )
                self.label(box, text, "Muted.TLabel")
            if len(mistakes) > 5:
                self.label(box, f"...and {len(mistakes) - 5} more", "Muted.TLabel")

        self.button(box, "Play again", lambda: self.app.show(SetupScreen)).pack_configure(
            pady=(20, 5)
        )
        self.button(box, "Main menu", lambda: self.app.show(MainMenu), "Secondary.TButton")
        self.button(box, "Exit", self.app.confirm_exit, "Danger.TButton")
