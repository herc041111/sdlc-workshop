"""A smoke test of the Streamlit view. Logic is tested in test_core.py; this only checks
that the UI is wired to it."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from poll import store

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def poll_file(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DEFAULT_PATH", tmp_path / "poll.json")


def run_app():
    return AppTest.from_file(APP, default_timeout=30).run()


def test_create_a_poll_then_vote():
    app = run_app()
    app.text_input[0].input("Lunch?")
    app.text_area[0].input("Pizza\nSushi")
    app.button[0].click().run()

    assert app.subheader[0].value == "Lunch?"

    app.radio[0].set_value("Sushi")
    app.button[0].click().run()

    assert store.load()["votes"] == {"Pizza": 0, "Sushi": 1}
    assert "1 votes so far" in app.caption[0].value


def test_new_poll_says_no_votes_yet():
    app = run_app()
    app.text_input[0].input("Lunch?")
    app.text_area[0].input("Pizza\nSushi")
    app.button[0].click().run()

    assert app.caption[0].value == "No votes yet — be the first!"


def test_results_list_shows_share_and_mark():
    app = run_app()
    app.text_input[0].input("Lunch?")
    app.text_area[0].input("Pizza\nSushi\nSalad")
    app.button[0].click().run()
    for choice in ["Pizza", "Pizza", "Sushi"]:
        app.radio[0].set_value(choice)
        app.button[0].click().run()

    lines = [md.value for md in app.markdown]
    assert "Pizza — 2 votes (67%) 🏆" in lines
    assert "Sushi — 1 votes (33%) 👎" in lines
    assert "Salad — 0 votes (0%) not voted yet" in lines


def test_invalid_poll_shows_an_error():
    app = run_app()
    app.text_input[0].input("Lunch?")
    app.text_area[0].input("Pizza")
    app.button[0].click().run()

    assert "two options" in app.error[0].value
    assert store.load() is None


def create_and_vote(options, votes):
    app = run_app()
    app.text_input[0].input("Lunch?")
    app.text_area[0].input("\n".join(options))
    app.button[0].click().run()
    for choice in votes:
        app.radio[0].set_value(choice)
        app.button[0].click().run()
    return [md.value for md in app.markdown]


def test_results_list_shows_draw_mark():
    lines = create_and_vote(["Pizza", "Sushi"], ["Pizza", "Sushi"])

    assert lines == ["Pizza — 1 votes (50%) 🤝", "Sushi — 1 votes (50%) 🤝"]


def test_new_poll_lists_options_without_marks():
    lines = create_and_vote(["Pizza", "Sushi"], [])

    assert lines == ["Pizza — 0 votes (0%)", "Sushi — 0 votes (0%)"]


def test_results_list_follows_creation_order():
    lines = create_and_vote(["Pizza", "Sushi", "Salad"], ["Salad"])

    assert [line.split(" — ")[0] for line in lines] == ["Pizza", "Sushi", "Salad"]


def test_option_names_are_shown_literally_not_as_markdown():
    lines = create_and_vote(["*Pizza*", "# Sushi", "![x](http://example.test/p.png)"], ["*Pizza*"])

    assert lines == [
        r"\*Pizza\* — 1 votes (100%) 🏆",
        r"\# Sushi — 0 votes (0%) not voted yet",
        r"\!\[x\]\(http://example\.test/p\.png\) — 0 votes (0%) not voted yet",
    ]


def test_question_and_vote_options_are_shown_literally():
    app = run_app()
    app.text_input[0].input("# Lunch?")
    app.text_area[0].input("*Pizza*\n![x](http://example.test/p.png)")
    app.button[0].click().run()

    assert app.subheader[0].value == r"\# Lunch?"
    assert app.radio[0].options == [r"\*Pizza\*", r"\!\[x\]\(http://example\.test/p\.png\)"]

    app.radio[0].set_value("*Pizza*")
    app.button[0].click().run()

    assert store.load()["votes"]["*Pizza*"] == 1
