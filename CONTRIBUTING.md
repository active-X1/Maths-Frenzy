# Contributing

Thanks for helping improve Maths Frenzy!

## Setup

```bash
git clone https://github.com/<your-username>/Maths-Frenzy.git
cd Maths-Frenzy
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[web,dev]"
```

## Checks

```bash
pytest          # tests
ruff check .    # lint
ruff format .   # format
mypy            # type-check the core
```

## Guidelines

- **Game rules and maths belong in `maths_frenzy.core`**, never in an interface.
  Interfaces only render state and forward input. If you add a rule, add a test.
- `core` must stay free of third-party and GUI imports.
- Keep each interface working on its own: the CLI and desktop app must not
  require NiceGUI.
- User-facing text shared by several interfaces goes in `core/content.py`.
- Update `CHANGELOG.md` for user-visible changes.
