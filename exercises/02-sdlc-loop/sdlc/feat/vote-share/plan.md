# Plan: Vote share percentages and leader marks

Spec: [spec.md](spec.md)

## Approach

Two new pure functions in `poll/core.py`, next to `tally()` and `total_votes()`. Both take a
`Poll`, don't mutate it, and return a list in creation order:

- `percentages(poll) -> list[tuple[str, int]]`: whole-number shares by largest remainder.
  Floor each `votes * 100 // total`, then give the leftover points, one each, to the options
  with the largest remainder (`votes * 100 % total`), ties going to the option created
  first. Integer arithmetic only, so there are no float rounding surprises. Zero votes → all 0.
- `standings(poll) -> list[tuple[str, str | None]]`: `"leader"`, `"draw"`, `"loser"`,
  `"unvoted"` (0 votes while others have votes) or `None`, decided from vote counts, never
  from rounded percentages. Zero votes → all `None`.

Two functions rather than one `results()`: rounding and ranking are independent rules, each
gets its own tests, and ranking can't accidentally read rounded shares. The status is a
plain string, not an emoji: `poll/core.py` stays free of presentation, and `app.py` maps
`leader → 🏆`, `draw → 🤝`, `loser → 👎`, `unvoted → not voted yet`.

`app.py` stays thin: under the bar chart it zips `tally()`, `percentages()` and
`standings()` into one line per option, `<option> — <n> votes (<p>%) <mark>`, and swaps the
caption to "No votes yet — be the first!" when `total_votes()` is 0.

Checks before every commit: `uv run python -m pytest -q` and `uv run python -m ruff check .`

## Tasks

### Task 1: Percentages that always add up to 100

- Acceptance criteria: spec #1, #2, #3, #4 (percentages part), #8, #9.
- Test that proves it (in `tests/test_core.py`, written first):
  - `test_percentages_add_up_to_100` (e.g. 2 / 1 → 67 / 33, 1 / 2 → 33 / 67)
  - `test_percentages_give_leftover_point_to_first_created_on_tie` (1 / 1 / 1 → 34 / 33 / 33)
  - `test_percentages_with_a_zero_vote_option` (1 / 1 / 1 / 0 → 34 / 33 / 33 / 0)
  - `test_percentages_are_zero_with_no_votes`
  - `test_percentages_keep_creation_order`, `test_percentages_leave_the_poll_unchanged`
- Files: `poll/core.py`, `tests/test_core.py`. Size: S.

### Task 2: Leader, draw and loser standings

- Acceptance criteria: spec #4 (no marks part), #5, #6, #7, #8, #9.
- Test that proves it (in `tests/test_core.py`, written first):
  - `test_standings_single_leader_others_lose` (3 / 1 / 0 → leader / loser / loser)
  - `test_standings_tie_for_first_is_a_draw` (2 / 2 / 1 → draw / draw / loser, including a
    3-way tie)
  - `test_standings_everyone_tied_is_all_draw` (1 / 1 / 1 → draw ×3, even though the
    percentages are 34 / 33 / 33)
  - `test_standings_are_none_with_no_votes`
  - `test_standings_leave_the_poll_unchanged`
- Files: `poll/core.py`, `tests/test_core.py`. Size: S.

### Task 3: Show the results list, "not voted yet" and the empty-poll caption

Extended after the spec amendment: an option with 0 votes in a poll that has votes is
"not voted yet", not a loser. That rule is business logic, so it lands in `standings()`
first (test-first in `tests/test_core.py`), then the view displays it.

- Acceptance criteria: spec #5, #6, #10, #11, #12.
- Test that proves it:
  - core (`tests/test_core.py`, written first):
    - `test_standings_zero_vote_option_is_unvoted_beside_a_draw` (1 / 1 / 0 → draw / draw /
      unvoted)
    - `test_standings_single_leader_others_lose` updated: 3 / 1 / 0 → leader / loser /
      unvoted
    - 2 / 2 / 1 still gives draw / draw / loser (unchanged)
  - wiring (`tests/test_app.py`):
    - in a Pizza/Sushi/Salad poll after votes Pizza, Pizza, Sushi, the page shows
      `Pizza — 2 votes (67%) 🏆`, `Sushi — 1 votes (33%) 👎` and
      `Salad — 0 votes (0%) not voted yet`
    - a new poll shows the caption "No votes yet — be the first!"
    - the existing `test_create_a_poll_then_vote` still passes ("1 votes so far")
- Files: `poll/core.py`, `tests/test_core.py`, `app.py`, `tests/test_app.py`. Size: S/M.
  Depends on tasks 1 and 2.

### Checkpoint: after task 3

- Full suite and ruff clean; run the app (`uv run python -m streamlit run app.py`) and check
  by eye: zero votes, a clear leader, a draw, and a 1 / 1 / 0 draw with "not voted yet".

## Risks

- **Largest-remainder tie-break is easy to get subtly wrong** (e.g. sorting unstably or by
  name). Mitigation: the 1 / 1 / 1 and 1 / 1 / 1 / 0 tests pin the exact output.
- **Standings computed from percentages by mistake** would put 🏆 on the 34% option in a
  1 / 1 / 1 tie. Mitigation: `test_standings_everyone_tied_is_all_draw`.
- **Finding the results lines in `AppTest`.** The list is rendered with `st.markdown` (or
  `st.write`), and the test reads `app.markdown`. If emoji or the em dash don't match
  exactly, the test fails loudly, which is what we want.
- **"1 votes" grammar** stays as it is today; pluralization is out of scope.

## SDLC command coverage

- [x] /sdlc:spec: approved 2026-10-23 after 9 questions
- [x] /sdlc:plan: 3 tasks
- [x] /sdlc:build: 3 tasks, one commit each; task 3 extended by the 2026-10-23 spec amendment
- [ ] /sdlc:test
- [ ] /sdlc:review
- [ ] /sdlc:code-simplify

## Test evidence

- 2026-10-23 17:10 · task 1 RED · `uv run python -m pytest tests/test_core.py -q` → collection error: cannot import name 'percentages' from 'poll.core' (expected)
- 2026-10-23 17:12 · task 1 GREEN · `uv run python -m pytest -q` → 24 passed; `uv run python -m ruff check .` → 2 × B905 (zip without strict=)
- 2026-10-23 17:13 · task 1 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 24 passed, All checks passed!
- 2026-10-23 17:18 · task 2 RED · `uv run python -m pytest tests/test_core.py -q` → collection error: cannot import name 'standings' from 'poll.core' (expected)
- 2026-10-23 17:18 · task 2 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 30 passed, All checks passed!
- 2026-10-23 19:19 · task 3 RED · `uv run python -m pytest -q` → 4 failed, 29 passed: 2 core standings tests got 'loser' instead of 'unvoted'; 2 app tests found no results list or new caption (expected)
- 2026-10-23 19:20 · task 3 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 33 passed, All checks passed!
- 2026-10-23 19:20 · task 3 checkpoint · real `app.py` driven through `AppTest` (scratchpad script): Pizza/Apple/Orange 1/1/0 → `50% 🤝`, `50% 🤝`, `0% not voted yet`; 2/2/1 → `40% 🤝`, `40% 🤝`, `20% 👎`; empty poll caption "No votes yet — be the first!". Browser check by eye not done.
