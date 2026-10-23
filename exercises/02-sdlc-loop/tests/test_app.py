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
