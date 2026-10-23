"""Poll logic as plain functions over plain data.

Nothing here touches files or Streamlit. That's what makes it easy to test: every
function takes a poll and returns a value or a new poll.
"""

from __future__ import annotations

from typing import TypedDict


class Poll(TypedDict):
    question: str
    options: list[str]
    votes: dict[str, int]


def create_poll(question: str, options: list[str]) -> Poll:
    """Return a new poll with zero votes. Surrounding whitespace and blank options are dropped."""
    question = question.strip()
    cleaned = [option.strip() for option in options if option.strip()]
    if not question:
        raise ValueError("A poll needs a question.")
    if len(cleaned) < 2:
        raise ValueError("A poll needs at least two options.")
    if len(set(cleaned)) != len(cleaned):
        raise ValueError("Options must be unique.")
    return {"question": question, "options": cleaned, "votes": {option: 0 for option in cleaned}}


def vote(poll: Poll, option: str) -> Poll:
    """Return a copy of the poll with one more vote for `option`."""
    if option not in poll["votes"]:
        raise ValueError(f"Unknown option: {option!r}")
    votes = {**poll["votes"], option: poll["votes"][option] + 1}
    return {**poll, "votes": votes}


def tally(poll: Poll) -> list[tuple[str, int]]:
    """Vote counts per option, in the order the options were created."""
    return [(option, poll["votes"][option]) for option in poll["options"]]


def total_votes(poll: Poll) -> int:
    return sum(poll["votes"].values())


def percentages(poll: Poll) -> list[tuple[str, int]]:
    """Whole-number share of the vote per option, in creation order, adding up to 100.

    Largest remainder: round every share down, then hand the leftover points one each to
    the largest remainders, ties going to the option created first. All 0 with no votes.
    """
    total = total_votes(poll)
    counts = tally(poll)
    if total == 0:
        return [(option, 0) for option, _ in counts]
    shares = [votes * 100 // total for _, votes in counts]
    by_remainder = sorted(range(len(counts)), key=lambda i: -(counts[i][1] * 100 % total))
    for i in by_remainder[: 100 - sum(shares)]:
        shares[i] += 1
    return [(option, share) for (option, _), share in zip(counts, shares, strict=True)]
