import pytest

from poll.core import create_poll, percentages, standings, tally, total_votes, vote


def make_poll():
    return create_poll("Lunch?", ["Pizza", "Sushi", "Salad"])


def test_create_poll_starts_with_zero_votes():
    poll = make_poll()

    assert poll["question"] == "Lunch?"
    assert poll["options"] == ["Pizza", "Sushi", "Salad"]
    assert poll["votes"] == {"Pizza": 0, "Sushi": 0, "Salad": 0}


def test_create_poll_trims_whitespace_and_drops_blank_options():
    poll = create_poll("  Lunch?  ", [" Pizza ", "", "   ", "Sushi"])

    assert poll["question"] == "Lunch?"
    assert poll["options"] == ["Pizza", "Sushi"]


def test_create_poll_needs_a_question():
    with pytest.raises(ValueError, match="question"):
        create_poll("   ", ["Pizza", "Sushi"])


def test_create_poll_needs_two_options():
    with pytest.raises(ValueError, match="two options"):
        create_poll("Lunch?", ["Pizza", ""])


def test_create_poll_rejects_duplicate_options():
    with pytest.raises(ValueError, match="unique"):
        create_poll("Lunch?", ["Pizza", "Pizza"])


def test_vote_adds_one_vote_to_the_option():
    poll = vote(make_poll(), "Sushi")

    assert poll["votes"]["Sushi"] == 1
    assert poll["votes"]["Pizza"] == 0


def test_vote_leaves_the_original_poll_unchanged():
    original = make_poll()

    vote(original, "Pizza")

    assert original["votes"]["Pizza"] == 0


def test_vote_for_an_unknown_option_raises():
    with pytest.raises(ValueError, match="Unknown option"):
        vote(make_poll(), "Burgers")


def test_tally_keeps_the_order_options_were_created_in():
    poll = vote(vote(make_poll(), "Salad"), "Salad")

    assert tally(poll) == [("Pizza", 0), ("Sushi", 0), ("Salad", 2)]


def test_total_votes_counts_every_vote():
    poll = vote(vote(vote(make_poll(), "Pizza"), "Sushi"), "Pizza")

    assert total_votes(poll) == 3


def test_total_votes_is_zero_for_a_new_poll():
    assert total_votes(make_poll()) == 0


def poll_with_votes(counts):
    """A poll whose options A, B, C... have the given vote counts."""
    options = [chr(ord("A") + i) for i in range(len(counts))]
    poll = create_poll("Lunch?", options)
    return {**poll, "votes": dict(zip(options, counts, strict=True))}


def test_percentages_add_up_to_100():
    assert percentages(poll_with_votes([2, 1])) == [("A", 67), ("B", 33)]
    assert percentages(poll_with_votes([1, 2])) == [("A", 33), ("B", 67)]


def test_percentages_give_leftover_point_to_first_created_on_tie():
    assert percentages(poll_with_votes([1, 1, 1])) == [("A", 34), ("B", 33), ("C", 33)]


def test_percentages_with_a_zero_vote_option():
    assert percentages(poll_with_votes([1, 1, 1, 0])) == [
        ("A", 34),
        ("B", 33),
        ("C", 33),
        ("D", 0),
    ]


def test_percentages_always_total_100_when_there_are_votes():
    for counts in ([1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [5, 3, 2, 1], [0, 7, 0], [2, 2, 2, 1]):
        assert sum(p for _, p in percentages(poll_with_votes(counts))) == 100


def test_percentages_are_zero_with_no_votes():
    assert percentages(make_poll()) == [("Pizza", 0), ("Sushi", 0), ("Salad", 0)]


def test_percentages_keep_creation_order():
    poll = vote(vote(make_poll(), "Salad"), "Salad")

    assert [option for option, _ in percentages(poll)] == ["Pizza", "Sushi", "Salad"]


def test_percentages_leave_the_poll_unchanged():
    poll = poll_with_votes([1, 1, 1])
    before = {**poll, "votes": dict(poll["votes"]), "options": list(poll["options"])}

    percentages(poll)

    assert poll == before


def test_standings_single_leader_others_lose():
    assert standings(poll_with_votes([3, 1, 0])) == [
        ("A", "leader"),
        ("B", "loser"),
        ("C", "unvoted"),
    ]


def test_standings_zero_vote_option_is_unvoted_beside_a_draw():
    assert standings(poll_with_votes([1, 1, 0])) == [
        ("A", "draw"),
        ("B", "draw"),
        ("C", "unvoted"),
    ]


def test_standings_tie_for_first_is_a_draw():
    assert standings(poll_with_votes([2, 2, 1])) == [
        ("A", "draw"),
        ("B", "draw"),
        ("C", "loser"),
    ]


def test_standings_three_way_tie_for_first_is_a_draw():
    assert standings(poll_with_votes([1, 3, 3, 3])) == [
        ("A", "loser"),
        ("B", "draw"),
        ("C", "draw"),
        ("D", "draw"),
    ]


def test_standings_everyone_tied_is_all_draw():
    # Percentages are 34 / 33 / 33 here, but standings follow vote counts.
    assert standings(poll_with_votes([1, 1, 1])) == [("A", "draw"), ("B", "draw"), ("C", "draw")]


def test_standings_are_none_with_no_votes():
    assert standings(make_poll()) == [("Pizza", None), ("Sushi", None), ("Salad", None)]


def test_standings_leave_the_poll_unchanged():
    poll = poll_with_votes([2, 2, 1])
    before = {**poll, "votes": dict(poll["votes"]), "options": list(poll["options"])}

    standings(poll)

    assert poll == before


def test_percentages_are_whole_numbers():
    for counts in ([2, 1], [1, 1, 1], [5, 3, 2, 1], [0, 0]):
        assert all(type(p) is int for _, p in percentages(poll_with_votes(counts)))


def test_percentages_spread_several_leftover_points_by_remainder():
    # 33.3 / 16.7 ×4: three leftover points go to the largest remainders (B, C, D),
    # not to A, and E misses out because it was created last.
    assert percentages(poll_with_votes([2, 1, 1, 1, 1])) == [
        ("A", 33),
        ("B", 17),
        ("C", 17),
        ("D", 17),
        ("E", 16),
    ]


def test_standings_marks_every_voted_non_leader_as_loser():
    assert standings(poll_with_votes([3, 1, 1, 0])) == [
        ("A", "leader"),
        ("B", "loser"),
        ("C", "loser"),
        ("D", "unvoted"),
    ]


def test_standings_keep_creation_order():
    poll = vote(vote(make_poll(), "Salad"), "Sushi")

    assert standings(poll) == [("Pizza", "unvoted"), ("Sushi", "draw"), ("Salad", "draw")]
