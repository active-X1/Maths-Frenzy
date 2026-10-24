"""Tiny terminal helper: ANSI colours and input with a timeout. Standard library only."""

from __future__ import annotations

import os
import select
import sys
import time

__all__ = ["BOLD", "CYAN", "DIM", "GREEN", "RED", "YELLOW", "Console"]

BOLD = "1"
DIM = "2"
RED = "31"
GREEN = "32"
YELLOW = "33"
CYAN = "36"


class Console:
    """Reads and writes to the terminal.

    Interfaces talk to this class rather than to ``print``/``input`` directly,
    which keeps the CLI easy to test (subclass it and script the answers).
    """

    def __init__(self, color: bool | None = None) -> None:
        self.color = _supports_color() if color is None else color

    def style(self, text: str, *codes: str) -> str:
        if not self.color or not codes:
            return text
        return f"\033[{';'.join(codes)}m{text}\033[0m"

    def print(self, text: str = "", *, end: str = "\n") -> None:
        sys.stdout.write(text + end)
        sys.stdout.flush()

    def ask(self, prompt: str, timeout: float | None = None) -> str | None:
        """Prompt the user and return their line.

        Returns ``None`` if ``timeout`` seconds pass with no answer. Timeouts are
        only enforced on an interactive terminal; piped input is read normally.

        Raises:
            EOFError: if standard input is closed.
        """
        sys.stdout.write(prompt)
        sys.stdout.flush()
        if timeout is None or not sys.stdin.isatty():
            return _read_line()
        if sys.platform == "win32":
            return _read_line_windows(timeout)
        return _read_line_posix(timeout)


def _read_line() -> str:
    line = sys.stdin.readline()
    if line == "":
        raise EOFError
    return line.rstrip("\r\n")


def _read_line_posix(timeout: float) -> str | None:
    ready, _, _ = select.select([sys.stdin], [], [], max(timeout, 0))
    if not ready:
        sys.stdout.write("\n")
        try:  # drop any half-typed text so it doesn't leak into the next prompt
            import termios

            termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
        except (ImportError, OSError, ValueError):
            pass
        return None
    return _read_line()


def _read_line_windows(timeout: float) -> str | None:  # pragma: no cover - Windows only
    import msvcrt

    deadline = time.monotonic() + timeout
    chars: list[str] = []
    while time.monotonic() < deadline:
        if not msvcrt.kbhit():
            time.sleep(0.02)
            continue
        char = msvcrt.getwche()
        if char in ("\r", "\n"):
            sys.stdout.write("\n")
            return "".join(chars)
        if char == "\x03":
            raise KeyboardInterrupt
        if char in ("\x00", "\xe0"):  # arrow/function keys send a second byte
            msvcrt.getwch()
        elif char == "\b":
            if chars:
                chars.pop()
                sys.stdout.write(" \b")
        else:
            chars.append(char)
    sys.stdout.write("\n")
    return None


def _supports_color() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":  # pragma: no cover - Windows only
        return _enable_windows_ansi()
    return True


def _enable_windows_ansi() -> bool:  # pragma: no cover - Windows only
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except (AttributeError, OSError):
        return False
