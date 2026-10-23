# Spec: Vote share percentages and leader marks

Status: Approved (2026-10-23)

Amended 2026-10-23 at the user's request, during task 3: once there are votes, an option
with 0 votes shows "not voted yet" instead of 👎 (criteria 5, 6, 10 and 12).

Amended 2026-10-23 at the user's request, after review finding #2: text typed by users is
shown literally everywhere it appears, not only in the results list (criterion 13).

## Objective

People watching a live poll should see at a glance each option's share of the vote and who
is winning. Under the existing bar chart, each option gets one line with its votes, a
whole-number percentage, and a mark: 🏆 for a clear leader, 🤝 for options tied for first,
👎 for every other option that has votes, and "not voted yet" for an option with no votes.

## Scope

In scope:
- Pure functions in `poll/core.py` that compute each option's percentage and its standing
  (leader, draw, loser or not voted yet), with tests in `tests/test_core.py` written first.
- A results list in `app.py`, under the bar chart, one line per option in creation order,
  e.g. `Pizza — 5 votes (42%) 🏆`.
- With zero votes, the caption "No votes yet — be the first!" replaces "0 votes so far".
- A wiring check in `tests/test_app.py` that the results list is shown.
- Showing user-typed text literally (Markdown escaped) in the poll question, the vote
  options and the results list.

Out of scope:
- Decimal places in percentages.
- Sorting results by votes. The order stays the order options were created in.
- Any change to the bar chart.
- Auto-refresh of results.
- Any change to voting, poll creation, reset or `poll/store.py`.

## Success criteria

1. Given a poll with at least one vote, when percentages are computed, then each is a whole
   number and together they add up to exactly 100.
2. Given votes 1 / 1 / 1, when percentages are computed, then they are 34 / 33 / 33: shares
   are rounded down, leftover points go to the largest fractional parts, and when fractional
   parts tie, the option created first gets the point.
3. Given other uneven splits, percentages follow the same rule and still add up to 100:
   2 / 1 → 67 / 33, 1 / 2 → 33 / 67, and 1 / 1 / 1 / 0 → 34 / 33 / 33 / 0.
4. Given a poll with zero votes, then every option's percentage is 0 and no option has a
   mark.
5. Given one option has strictly more votes than every other, then that option is marked
   🏆 and every other option with at least one vote is marked 👎.
6. Given two or more options share the highest vote count (e.g. 2 / 2 / 1), then each of
   them is marked 🤝, none is marked 🏆, and the rest with at least one vote are marked 👎.
7. Given every option has the same non-zero count, then every option is marked 🤝 and none
   is marked 👎.
8. Results are returned in the order the options were created, whatever the vote counts.
9. The core functions don't change the poll they are given.
10. In the app, below the bar chart, each option is listed as
    `<option> — <n> votes (<p>%) <mark>`, where the mark is 🏆, 🤝, 👎 or "not voted yet",
    and there is no mark when the poll has no votes.
11. In the app, with zero votes the caption reads "No votes yet — be the first!"; with
    votes it still reads "<n> votes so far".
12. Given the poll has votes and an option has 0 votes, then that option shows 0% and
    "not voted yet", never 👎: 1 / 1 / 0 → 🤝 / 🤝 / not voted yet, and
    3 / 1 / 0 → 🏆 / 👎 / not voted yet.
13. Given a question or option typed with Markdown in it (e.g. `# Lunch?`, `*Pizza*`,
    `![x](http://…)`), then the question heading, the vote options and the results list show
    it as typed, never as a heading, emphasis, link or image, and voting for such an option
    still counts it under its original name.

## Edge cases and decisions

| Case | Decision | Why |
|---|---|---|
| Rounding | Whole-number percentages | User wants readable shares, no decimals. |
| Total of the shown shares | Always exactly 100 when there are votes, no exceptions | User chose "100%, without exceptions". |
| Rounding method | Largest remainder: round every share down, give the leftover points one at a time to the largest fractional parts | Smallest change from the true shares that still adds to 100. |
| Tied fractional parts | The option created first gets the extra point (1 / 1 / 1 → 34 / 33 / 33) | Deterministic and easy to test; user confirmed. |
| Zero votes | Every option shows 0%, no marks; caption "No votes yet — be the first!" replaces "0 votes so far" | User asked for 0% plus a hint that voting hasn't started. |
| Single clear leader | 🏆 on the leader | Original request. |
| Tie for first (any number of options) | 🤝 on every tied leader, no 🏆 | User: a draw is not a leader. Applies to 2-way, 3-way and larger ties. |
| Options not in first place | 👎 on each that has at least one vote | User chose a loser mark for every non-leader that was voted for. |
| Everyone tied | All 🤝, no 👎 | Nobody is behind. |
| Marks follow vote counts, not percentages | 1 / 1 / 1 shows 34 / 33 / 33 but all are 🤝 | The extra rounding point must not create a fake leader. |
| Option with zero votes while others have votes | 0% and "not voted yet" (plain text, no icon), whether the lead is a 🏆 or a 🤝 | Amended: user found 1 / 1 / 0 showing 👎 on an option nobody voted for; 0 votes means not voted yet, not losing. |
| Order | Creation order | Rows don't jump around while the room watches votes come in. |
| Display | Text list under the existing bar chart | User kept the chart and added a line per option. |
| Markdown in user text | Escaped in `st.subheader`, `st.radio` labels (via `format_func`, so the stored vote keeps the raw name) and the results list | Review finding #2; `st.subheader` renders full Markdown and `st.radio` labels render links and images. User asked to fix it on this branch. |
| Invalid input | None new: polls already have at least two unique options and votes only for known options (`create_poll`, `vote`) | Existing validation covers it. |

## Open questions

- None.

## Decisions

- No ADR. Largest-remainder rounding was a user choice with no lasting architectural impact,
  and it is recorded above.
