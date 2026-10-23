# Review: Vote share percentages and leader marks

Reviewer: `code-reviewer` agent, fresh context, 2026-10-23. Scope: `git diff main...HEAD`
(poll/core.py, app.py, tests/), spec.md (with the 2026-10-23 amendment), plan.md.
Checks at review time: `uv run python -m pytest -q` → 40 passed; `uv run python -m ruff check .` → clean.

Verdict: **request changes** (one Important finding), everything else is a suggestion.
Spec alignment: all 12 criteria and the amendment implemented; nothing outside scope changed.
Performance: no findings.

## Findings

| # | Severity | Axis | Where | Finding | Fix | Status |
|---|---|---|---|---|---|---|
| 1 | Important | Correctness (tests) | `tests/test_core.py:74` (`poll_with_votes`), `poll/core.py:59` | "Ties go to the option created first" (spec #2) is not really tested: the helper names options A, B, C…, so creation order and alphabetical order always agree. The reviewer broke ties by name instead and all 40 tests still passed. The plan names exactly this risk. | Add a tie test whose creation order isn't alphabetical, e.g. Sushi / Pizza / Salad with 1 vote each → 34 / 33 / 33 for Sushi / Pizza / Salad. | fixed: `test_percentages_tie_break_follows_creation_order_not_name`; passes as built, fails when ties are broken by name |
| 2 | Suggestion | Security | `app.py:44` | Option names typed by users go through `st.markdown`, so Markdown in them takes effect: `# Pizza` becomes a heading, `C++*` is mangled, `![x](https://…)` loads an outside image in every viewer's browser, `[x](…)` becomes a link. | Escape Markdown characters in the option name (or show the list with `st.text`), plus a wiring test with an option like `*Pizza*`. | fixed: `escape_markdown()` in `app.py`; `test_option_names_are_shown_literally_not_as_markdown` failed first, then passed |
| 3 | Suggestion | Correctness | `poll/core.py:54`, `poll/core.py:73` | `percentages()` gets the total from `poll["votes"]` but the counts from `poll["options"]`. If the two ever disagree (e.g. a hand-edited store file), the shares no longer add to 100. This can't happen through `create_poll` and `vote`. | Compute the total from `tally(poll)` so both numbers come from the same place. | won't fix: user's call at review; can't happen via create_poll/vote, and the store is out of scope |
| 4 | Suggestion | Readability | `poll/core.py:65`, `app.py:9` | The four standing values are bare strings that `core.py` and `MARKS` in `app.py` must keep in sync; a typo shows only as a `KeyError` when the app runs. | Add `Standing = Literal["leader", "draw", "loser", "unvoted"]` in core and use it as the return type. | won't fix: user's call at review; 4 values, and a typo already fails loudly in the app tests |
| 5 | Suggestion | Readability | `tests/test_app.py:72` | The `create_and_vote` helper sits halfway down the file, and two tests above it repeat the same steps by hand. | Move it next to `run_app` and use it in `test_new_poll_says_no_votes_yet` and `test_results_list_shows_share_and_mark`. | won't fix now: user's call at review; candidate for /sdlc:code-simplify |
| 6 | Suggestion | Architecture | `tests/test_app.py:95` | `test_results_list_follows_creation_order` checks ordering, which is a core rule already covered by both core order tests. `CLAUDE.md` limits `test_app.py` to wiring. | Drop the test, or fold its assertion into an existing app test. | won't fix now: user's call at review; candidate for /sdlc:code-simplify |
| 7 | Suggestion | Readability | `app.py:44` | `.rstrip()` is redundant: Streamlit already trims trailing whitespace (found in the /sdlc:test mutation check, confirmed by the reviewer). | Remove it in /sdlc:code-simplify. | deferred to /sdlc:code-simplify |

## Red Queen: rules that would have prevented these

Proposed only, not applied. Both break a pattern likely to come back.

1. **From #2, for `CLAUDE.md` › Conventions:**
   > Text typed by users (poll questions, option names) is never rendered as raw Markdown.
   > Escape it, or use a widget that shows plain text.

   The same exposure already exists outside this branch: the question goes through
   `st.subheader`. That's out of scope here, and a candidate follow-up.
2. **From #1, for `CLAUDE.md` › Conventions (tests):**
   > A test that checks order or tie-breaking uses names whose creation order isn't
   > alphabetical, so sorting by name can't pass by accident.

## Outcome

7 findings: 2 fixed (#1, #2), 4 won't fix (#3–#6, user's call), 1 deferred to /sdlc:code-simplify (#7).
