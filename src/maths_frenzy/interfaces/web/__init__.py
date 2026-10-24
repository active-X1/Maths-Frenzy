"""NiceGUI web interface for Maths Frenzy."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

__all__ = ["main"]


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``maths-frenzy web``."""
    parser = argparse.ArgumentParser(
        prog="maths-frenzy web", description="Maths Frenzy web app (NiceGUI)."
    )
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default: %(default)s)")
    parser.add_argument("--port", type=int, default=8080, help="port to listen on (default: %(default)s)")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser tab")
    args = parser.parse_args(argv)

    try:
        from .app import run
    except ImportError as exc:
        if exc.name is None or not exc.name.startswith("nicegui"):
            raise
        print(
            "The web interface needs NiceGUI, which is not installed.\n"
            "Install it with:  pip install 'maths-frenzy[web]'"
        )
        return 1

    run(host=args.host, port=args.port, show=not args.no_browser)
    return 0
