"""Tests for the simpler Textual widgets (EvalMeter, MoveInputBar, MoveHistory)."""

import asyncio

import chess

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input

from tui_ui.widgets.eval_meter import EvalMeter
from tui_ui.widgets.input import MoveInputBar
from tui_ui.widgets.move_history import MoveHistory


def _run_async(coro):
    asyncio.run(coro)


# --- EvalMeter (pure, no app needed) ---


def test_eval_render_positive():
    m = EvalMeter()
    m.score = 1.5
    assert m.render() == "Eval: +1.50"


def test_eval_render_negative():
    m = EvalMeter()
    m.score = -2.0
    assert m.render() == "Eval: -2.00"


def test_eval_render_zero():
    m = EvalMeter()
    m.score = 0.0
    assert m.render() == "Eval: +0.00"


def test_eval_render_string_verbatim():
    m = EvalMeter()
    m.score = "Mate in 3"
    assert m.render() == "Eval: Mate in 3"


def test_eval_update_eval_sets_score():
    m = EvalMeter()
    m.update_eval(2.5)
    assert m.score == 2.5


# --- MoveHistory (needs a mounted app for query_one) ---


class _HistoryApp(App):
    def compose(self) -> ComposeResult:
        yield MoveHistory(id="mh")


def test_history_first_move_starts_row():
    async def _run():
        app = _HistoryApp()
        async with app.run_test() as pilot:
            mh = app.query_one(MoveHistory)
            mh.add_move("e4")
            table = mh.query_one(DataTable)
            assert table.row_count == 1
            assert table.get_row_at(0) == ["1", "e4", ""]

    _run_async(_run())


def test_history_black_move_fills_row():
    async def _run():
        app = _HistoryApp()
        async with app.run_test() as pilot:
            mh = app.query_one(MoveHistory)
            mh.add_move("e4")
            mh.add_move("e5")
            table = mh.query_one(DataTable)
            assert table.row_count == 1
            assert table.get_row_at(0) == ["1", "e4", "e5"]

    _run_async(_run())


def test_history_new_pair_starts_new_row():
    async def _run():
        app = _HistoryApp()
        async with app.run_test() as pilot:
            mh = app.query_one(MoveHistory)
            mh.add_move("e4")
            mh.add_move("e5")
            mh.add_move("Nf3")
            table = mh.query_one(DataTable)
            assert table.row_count == 2
            assert table.get_row_at(1) == ["2", "Nf3", ""]

    _run_async(_run())


# --- MoveInputBar (needs a mounted app) ---


class _InputApp(App):
    def __init__(self):
        super().__init__()
        self.submitted: list[str] = []

    def compose(self) -> ComposeResult:
        yield MoveInputBar(id="bar")

    def on_move_input_bar_move_submitted(self, message):
        self.submitted.append(message.command)


def test_input_submits_move_and_clears():
    async def _run():
        app = _InputApp()
        async with app.run_test(size=(100, 30)) as pilot:
            inp = app.query_one("#bar").query_one(Input)
            await pilot.click(inp)
            await pilot.press("e", "4")
            await pilot.press("enter")
            assert app.submitted == ["e4"]
            assert inp.value == ""

    _run_async(_run())


def test_input_empty_submit_ignored():
    async def _run():
        app = _InputApp()
        async with app.run_test(size=(100, 30)) as pilot:
            inp = app.query_one("#bar").query_one(Input)
            await pilot.click(inp)
            await pilot.press("enter")
            assert app.submitted == []

    _run_async(_run())
