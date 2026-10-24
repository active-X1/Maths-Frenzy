"""Main window and screen navigation for the desktop interface."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox, ttk

from maths_frenzy import __version__
from maths_frenzy.core import Level, Operation
from maths_frenzy.core.content import APP_NAME

from .screens import MainMenu, Screen
from .theme import apply_theme

__all__ = ["MathsFrenzyApp"]


def _enable_high_dpi() -> None:  # pragma: no cover - Windows only
    """Ask Windows not to bitmap-scale the window (avoids blurry text)."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        pass


class MathsFrenzyApp(tk.Tk):
    """The application window. Holds shared state and swaps screens in and out."""

    def __init__(self) -> None:
        _enable_high_dpi()
        super().__init__()
        self.title(f"{APP_NAME} {__version__}")
        self.geometry("760x680")
        self.minsize(640, 600)
        apply_theme(self)

        self.player = "Player"
        self.level = Level.BEGINNER
        self.operation = Operation.ADDITION

        self._container = ttk.Frame(self, style="App.TFrame")
        self._container.pack(fill="both", expand=True)
        self._screen: Screen | None = None
        self.show(MainMenu)

    def show(self, screen_class: type[Screen], **kwargs: object) -> None:
        """Replace the visible screen with a new ``screen_class`` instance."""
        if self._screen is not None:
            self._screen.destroy()
        self._screen = screen_class(self._container, self, **kwargs)  # type: ignore[call-arg]
        self._screen.pack(fill="both", expand=True)

    def confirm_exit(self) -> None:
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()
