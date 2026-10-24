"""Tkinter desktop interface for Maths Frenzy."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

__all__ = ["main"]


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``maths-frenzy desktop``."""
    parser = argparse.ArgumentParser(
        prog="maths-frenzy desktop", description="Maths Frenzy desktop app (Tkinter)."
    )
    parser.parse_args(argv)

    try:
        import tkinter
    except ImportError:
        print(
            "Tkinter is not available in this Python installation.\n"
            "  Debian/Ubuntu: sudo apt install python3-tk\n"
            "  Fedora:        sudo dnf install python3-tkinter\n"
            "  macOS (brew):  brew install python-tk",
        )
        return 1

    from .app import MathsFrenzyApp

    try:
        app = MathsFrenzyApp()
    except tkinter.TclError as exc:
        print(f"Could not open a window: {exc}")
        return 1
    app.mainloop()
    return 0
