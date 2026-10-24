"""Keypad calculator widget, used as a screen and as an in-game pop-up."""

from __future__ import annotations

import tkinter as tk
from functools import partial
from tkinter import ttk

from maths_frenzy.core import CalculatorError, evaluate, format_number

from .theme import FONT_FAMILY

__all__ = ["KeypadCalculator", "open_calculator_window"]

KEYS = (
    ("C", "\u232b", "(", ")"),
    ("7", "8", "9", "\u00f7"),
    ("4", "5", "6", "\u00d7"),
    ("1", "2", "3", "\u2212"),
    ("0", ".", "=", "+"),
)


class KeypadCalculator(ttk.Frame):
    """A calculator with an expression display and an on-screen keypad."""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, style="App.TFrame", padding=12)
        self.display = tk.StringVar()
        self.status = tk.StringVar()

        self.entry = ttk.Entry(
            self, textvariable=self.display, justify="right", font=(FONT_FAMILY, 22)
        )
        self.entry.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 4), ipady=6)
        self.entry.bind("<Return>", lambda _event: self.press("="))
        self.entry.focus_set()

        ttk.Label(self, textvariable=self.status, style="Warning.TLabel").grid(
            row=1, column=0, columnspan=4, sticky="w", pady=(0, 8)
        )

        for row, keys in enumerate(KEYS, start=2):
            for column, key in enumerate(keys):
                style = "Accent.TButton" if key == "=" else "Key.TButton"
                ttk.Button(
                    self, text=key, style=style, width=5, command=partial(self.press, key)
                ).grid(row=row, column=column, sticky="nsew", padx=3, pady=3)
        for column in range(4):
            self.columnconfigure(column, weight=1)

    def press(self, key: str) -> None:
        self.status.set("")
        if key == "C":
            self.display.set("")
        elif key == "\u232b":
            self.display.set(self.display.get()[:-1])
        elif key == "=":
            try:
                self.display.set(format_number(evaluate(self.display.get())))
            except CalculatorError as exc:
                self.status.set(str(exc))
        else:
            self.display.set(self.display.get() + key)
        self.entry.icursor(tk.END)


def open_calculator_window(master: tk.Misc) -> tk.Toplevel:
    """Open the calculator in its own small window."""
    window = tk.Toplevel(master)
    window.title("Calculator")
    window.configure(background=master.cget("background"))
    window.resizable(False, False)
    KeypadCalculator(window).pack()
    return window
