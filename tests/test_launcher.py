import contextlib
import importlib.util
import io
import unittest

from maths_frenzy import __version__
from maths_frenzy.launcher import main


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(list(argv))
    return code, out.getvalue(), err.getvalue()


class LauncherTests(unittest.TestCase):
    def test_help(self) -> None:
        for argv in ([], ["--help"], ["-h"]):
            with self.subTest(argv=argv):
                code, out, _ = run(*argv)
                self.assertEqual(code, 0)
                for command in ("cli", "desktop", "web"):
                    self.assertIn(command, out)

    def test_version(self) -> None:
        self.assertEqual(run("--version"), (0, f"maths-frenzy {__version__}\n", ""))

    def test_unknown_command(self) -> None:
        code, _, err = run("nope")
        self.assertEqual(code, 2)
        self.assertIn("unknown command 'nope'", err)

    def test_dispatches_to_cli(self) -> None:
        code, out, _ = run("cli", "--no-color", "calc", "6*7")
        self.assertEqual((code, out), (0, "42\n"))

    @unittest.skipIf(importlib.util.find_spec("nicegui"), "NiceGUI is installed")
    def test_web_without_nicegui_gives_a_helpful_message(self) -> None:
        code, out, _ = run("web")
        self.assertEqual(code, 1)
        self.assertIn("pip install 'maths-frenzy[web]'", out)


if __name__ == "__main__":
    unittest.main()
