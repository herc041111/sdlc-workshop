# Pull request: feat/vote-share

- **Title:** `feat: vote share percentages with leader, draw and loser marks`
- **Base:** `main`
- **Head:** `feat/vote-share`
- **Why this file instead of a PR:** the GitHub CLI (`gh`) isn't installed on this machine,
  and `origin` points at `haco29/sdlc-workshop` (the upstream repo, not a fork), so write
  access couldn't be confirmed and nothing was pushed. To open a real PR: install `gh`
  (SETUP.md step 5), fork the repo (or point `origin` at your fork), push `feat/vote-share`,
  and paste the body below.

---

## Why

People watching a live poll should see at a glance each option's share of the vote and who
is winning. Under the bar chart, each option now gets one line with its votes, a
whole-number percentage, and a mark: 🏆 for a clear leader, 🤝 for options tied for first,
👎 for every other option that has votes, and "not voted yet" for an option with no votes.
Spec: [`spec.md`](exercises/02-sdlc-loop/sdlc/feat/vote-share/spec.md) (approved 2026-10-23,
amended twice the same day at the user's request).

## What changed

1. **Percentages that always add up to 100:** `percentages()` in `poll/core.py`, largest
   remainder with ties going to the option created first.
2. **Leader, draw and loser standings:** `standings()` in `poll/core.py`, decided from vote
   counts, never from rounded percentages.
3. **Results list, "not voted yet" and the empty-poll caption:** `app.py` renders one line
   per option under the chart; options with 0 votes are `"unvoted"`, not losers; an empty
   poll says "No votes yet — be the first!".
4. **Question and vote options shown literally:** user text is Markdown-escaped in the
   question, the radio labels (via `format_func`, so votes keep the raw name) and the
   results list.

Also: two conventions added to `CLAUDE.md` from the review (see Review).

## How it was tested

Latest Test evidence from [`plan.md`](exercises/02-sdlc-loop/sdlc/feat/vote-share/plan.md):

- 2026-10-23 19:40 · task 4 RED · `uv run python -m pytest -q tests/test_app.py::test_question_and_vote_options_are_shown_literally` → 1 failed: subheader showed `# Lunch?` unescaped (expected)
- 2026-10-23 19:40 · task 4 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 43 passed, All checks passed!
- 2026-10-23 19:42 · /sdlc:code-simplify start · `uv run python -m pytest -q && uv run python -m ruff check .` → 43 passed, All checks passed!
- 2026-10-23 19:43 · /sdlc:code-simplify final (after removing `.rstrip()` in `app.py`, no test edited) · `uv run python -m pytest -q && uv run python -m ruff check .` → 43 passed, All checks passed!
- 2026-10-23 19:45 · /sdlc:pr G4 · `uv run python -m pytest -q && uv run python -m ruff check .` → 43 passed, All checks passed!

Every task has a failing-then-passing run in the full log, and the `/sdlc:test` and review
steps broke the code on purpose to prove the new tests catch each mistake. The app was driven
through `AppTest`; it has not been checked by eye in a browser.

## Gates

| Gate | Result | Evidence |
|---|---|---|
| G1 Spec | pass | `spec.md:3` `Status: Approved (2026-10-23)`; no template text (the `<n>` placeholders are the specified display format) |
| G2 Plan | pass | `plan.md`: 4 tasks with acceptance criteria and tests, plus coverage and Test evidence sections |
| G3 Tasks | pass | `todo.md`: tasks 1–4 all ticked |
| G4 Evidence | pass | `uv run python -m pytest -q && uv run python -m ruff check .` → 43 passed, All checks passed! (2026-10-23 19:45, after the last code change) |
| G5 Alignment | pass | criteria 1–13 each map to code in `poll/core.py` / `app.py` and tests (mapped by the test-engineer agent, plus task 4 for #13); the only file outside the spec is `CLAUDE.md`, two review rules the user approved |
| G6 Coverage | pass | `plan.md:108-113`: all six commands ticked |

## Review

Fresh-context `code-reviewer`, 7 findings ([`review.md`](exercises/02-sdlc-loop/sdlc/feat/vote-share/review.md)):

- **Fixed:**
  - #1 (Important) the tie-break test passed even if ties were broken by name; new test with non-alphabetical names.
  - #2 option names rendered as Markdown; escaped, then widened to the question and radio labels (task 4).
  - #7 redundant `.rstrip()`, removed in code-simplify.
- **Won't fix (user's call):**
  - #3 total and counts from one source: can't diverge through `create_poll`/`vote`.
  - #4 a `Literal` type for standings: all four marks are covered by app tests.
  - #5 move the app test helper, and #6 drop a duplicate order test: both need test edits, which a no-behavior-change refactor mustn't make.
- **Rules added to `CLAUDE.md`:** user text is never rendered as raw Markdown; order and tie-break tests use names whose creation order isn't alphabetical.

## Out of scope

- Decimal places, sorting results by votes, changes to the bar chart, auto-refresh.
- Any change to voting, poll creation, reset or `poll/store.py`.
- "1 votes" pluralization (unchanged from before).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
