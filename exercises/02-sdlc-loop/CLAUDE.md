# Live Poll: agent instructions

A tiny Streamlit app used to practice the agentic SDLC
(`/sdlc:spec → /sdlc:plan → /sdlc:build → /sdlc:test → /sdlc:review → /sdlc:code-simplify → /sdlc:pr`).

## Conventions

- Business logic lives in `poll/core.py` as pure functions over plain data: no file I/O,
  no Streamlit imports. Return new values; don't mutate inputs.
- `poll/store.py` is the only module that touches the disk.
- `app.py` stays thin: load state, call `poll.core`, render. No business rules in the view.
- Every behavior in `poll/core.py` has a test in `tests/test_core.py`, written first.
- `tests/test_app.py` is a smoke test that the UI is wired to the core. Extend it only for
  wiring, not for logic.
- Text typed by users (poll questions, option names) is never rendered as raw Markdown.
  Escape it, or use a widget that shows plain text.
- A test that checks order or tie-breaking uses names whose creation order isn't
  alphabetical, so sorting by name can't pass by accident.

## Checks

Both must pass before every commit:

```bash
uv run python -m pytest -q
uv run python -m ruff check .
```

Always go through `uv run`: it uses this folder's environment, on Windows and macOS alike.
Don't create or activate a virtualenv by hand. Call tools as `python -m <tool>`, never as
`uv run pytest`: some company laptops block the tools' own `.exe` files but not Python.

## SDLC

Artifacts live in `sdlc/<branch>/` in this folder (spec, plan, todo, review), written by the
[agentic-sdlc](https://github.com/haco29/agentic-sdlc) commands. Work on a feature branch,
never on `main`.

## Data

Dummy data only. Never paste real customer data, card data or secrets into prompts,
fixtures or polls.
