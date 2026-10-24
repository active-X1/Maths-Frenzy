"""The ``maths-frenzy`` command: pick an interface and hand over to it."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from maths_frenzy import __version__
from maths_frenzy.core.content import APP_NAME, TAGLINE

__all__ = ["main"]

_HELP = f"""\
{APP_NAME} {__version__} - {TAGLINE}

usage: maths-frenzy COMMAND [ARGS...]

commands:
  cli       terminal interface (menu, quick play, calculator)
  desktop   desktop window built with Tkinter        (alias: gui)
  web       browser interface built with NiceGUI     (needs: pip install 'maths-frenzy[web]')

options:
  -h, --help     show this message
  -V, --version  show the version

Run 'maths-frenzy COMMAND --help' for the options of each interface.
"""


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help", "help"}:
        print(_HELP, end="")
        return 0
    command, rest = args[0], args[1:]
    if command in {"-V", "--version"}:
        print(f"maths-frenzy {__version__}")
        return 0
    if command == "cli":
        from maths_frenzy.interfaces.cli import main as run_cli

        return run_cli(rest)
    if command in {"desktop", "gui"}:
        from maths_frenzy.interfaces.desktop import main as run_desktop

        return run_desktop(rest)
    if command == "web":
        from maths_frenzy.interfaces.web import main as run_web

        return run_web(rest)
    print(f"maths-frenzy: unknown command '{command}'\n", file=sys.stderr)
    print(_HELP, end="", file=sys.stderr)
    return 2
