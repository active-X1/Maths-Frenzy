# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-10-24

A ground-up restructure of the original single-file Tkinter app.

### Added
- Installable `src/` layout package with a shared, dependency-free `core`.
- **Three interfaces** on top of the same core: terminal (`cli`), desktop
  (`desktop`, Tkinter) and browser (`web`, NiceGUI).
- `maths-frenzy` launcher plus one console script per interface.
- CLI: interactive menu, `play` quick-start with options, `calc` one-shot
  calculator, `howto`, practice mode (`--no-timer`) and live per-question timer.
- Result screens with accuracy, a rank, and a review of mistakes.
- Dark theme for the desktop app and light/dark toggle for the web app.
- Unit tests, `pyproject.toml`, Ruff/mypy configuration and GitHub Actions CI.
- MIT license, README, contributing guide.

### Changed
- Level, operation and scoring rules live in one place (`maths_frenzy.core`).
- Desktop app: registration, level and operation selection are one "New game"
  screen, and registration asks for a single nickname.
- Negative right-hand operands are shown in brackets, e.g. `5 + (-3)`.
- Invalid input no longer costs a question; the player can simply retry.
- Division answers are compared after rounding to two decimal places, so
  `0.333` is accepted for `1 / 3`.

### Fixed
- Division questions could divide by zero and crash the game.
- The calculator used `eval()` on arbitrary text; it now uses a safe parser.
- Two-number calculator crashed on division by zero.
- The timer expiring on a question read the answer field incorrectly.
- Opening the calculator during a game created a second, separate Tk root.

### Removed
- The pre-built `MathsFrenzy.exe` is no longer committed to the repository.
  Build it with PyInstaller (see the README) and publish it as a release asset.
