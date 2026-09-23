"""Tests for the Textual app screens (SetupScreen, GameScreen)."""

import asyncio
from typing import cast

import chess
import pytest

import tui_ui.app as appmod
from tui_ui.app import SetupScreen, GameScreen
from tui_ui.widgets.board import ChessSquare
from tui_ui.widgets.eval_meter import EvalMeter
from tui_ui.widgets.move_history import MoveHistory
from textual.app import App
from textual.widgets import Input, Button, RadioButton, DataTable


class _Host(App):
    pass


@pytest.fixture(autouse=True)
def _no_engine(monkeypatch):
    """Keep screen tests hermetic: no real Stockfish, no engine worker thread."""

    class _FakeEngine:
        def __init__(self, *args, **kwargs):
            raise FileNotFoundError("no stockfish binary in tests")

    monkeypatch.setattr(appmod, "StonkEngine", _FakeEngine)
    monkeypatch.setattr(GameScreen, "trigger_engine_turn", lambda self: None)


def _run_async(coro):
    asyncio.run(coro)


def _sel(gs, square):
    gs.on_chess_square_square_selected(ChessSquare.SquareSelected(square))


# --- SetupScreen ---


def test_setup_invalid_elo_not_dismissed():
    async def _run():
        app = _Host()
        async with app.run_test(size=(100, 30)) as pilot:
            app.push_screen(SetupScreen())
            await pilot.pause()
            scr = cast(SetupScreen, app.screen)
            scr.query_one("#elo_input", Input).value = "999"
            btn = scr.query_one("#btn_start", Button)
            scr.on_button_pressed(Button.Pressed(btn))
            await pilot.pause()
            assert isinstance(app.screen, SetupScreen)

    _run_async(_run())


def test_setup_non_numeric_elo_not_dismissed():
    async def _run():
        app = _Host()
        async with app.run_test(size=(100, 30)) as pilot:
            app.push_screen(SetupScreen())
            await pilot.pause()
            scr = cast(SetupScreen, app.screen)
            scr.query_one("#elo_input", Input).value = "abc"
            btn = scr.query_one("#btn_start", Button)
            scr.on_button_pressed(Button.Pressed(btn))
            await pilot.pause()
            assert isinstance(app.screen, SetupScreen)

    _run_async(_run())


def test_setup_below_range_not_dismissed():
    async def _run():
        app = _Host()
        async with app.run_test(size=(100, 30)) as pilot:
            app.push_screen(SetupScreen())
            await pilot.pause()
            scr = cast(SetupScreen, app.screen)
            scr.query_one("#elo_input", Input).value = "1000"
            btn = scr.query_one("#btn_start", Button)
            scr.on_button_pressed(Button.Pressed(btn))
            await pilot.pause()
            assert isinstance(app.screen, SetupScreen)

    _run_async(_run())


def test_setup_valid_elo_dismisses_with_white():
    async def _run():
        app = _Host()
        results = []
        async with app.run_test(size=(100, 30)) as pilot:
            app.push_screen(SetupScreen(), results.append)
            await pilot.pause()
            scr = cast(SetupScreen, app.screen)
            scr.query_one("#elo_input", Input).value = "1500"
            btn = scr.query_one("#btn_start", Button)
            scr.on_button_pressed(Button.Pressed(btn))
            await pilot.pause()
            assert results == [(1500, chess.WHITE)]
            assert not isinstance(app.screen, SetupScreen)

    _run_async(_run())


def test_setup_black_color():
    async def _run():
        app = _Host()
        results = []
        async with app.run_test(size=(100, 30)) as pilot:
            app.push_screen(SetupScreen(), results.append)
            await pilot.pause()
            scr = cast(SetupScreen, app.screen)
            scr.query_one("#elo_input", Input).value = "1800"
            scr.query_one("#radio_black", RadioButton).value = True
            await pilot.pause()
            btn = scr.query_one("#btn_start", Button)
            scr.on_button_pressed(Button.Pressed(btn))
            await pilot.pause()
            assert results == [(1800, chess.BLACK)]

    _run_async(_run())


def test_setup_quit_exits_app():
    async def _run():
        app = _Host()
        exited = []
        app.exit = lambda *args, **kwargs: exited.append(True)
        async with app.run_test(size=(100, 30)) as pilot:
            app.push_screen(SetupScreen())
            await pilot.pause()
            scr = cast(SetupScreen, app.screen)
            btn = scr.query_one("#btn_quit", Button)
            scr.on_button_pressed(Button.Pressed(btn))
            await pilot.pause()
            assert exited == [True]

    _run_async(_run())


# --- GameScreen ---


def test_game_select_own_piece_highlights():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            _sel(gs, chess.E2)
            await pilot.pause()
            assert gs.selected_square == chess.E2

    _run_async(_run())


def test_game_select_enemy_piece_not_selected():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            _sel(gs, chess.E7)  # black pawn, white to move
            await pilot.pause()
            assert gs.selected_square is None

    _run_async(_run())


def test_game_legal_move_made():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            _sel(gs, chess.E2)
            await pilot.pause()
            _sel(gs, chess.E4)
            await pilot.pause()
            assert gs.game.board.turn == chess.BLACK
            assert gs.game.board.piece_at(chess.E2) is None
            assert gs.game.board.piece_at(chess.E4) is not None
            assert gs.selected_square is None

    _run_async(_run())


def test_game_illegal_move_ignored():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            _sel(gs, chess.E2)
            await pilot.pause()
            _sel(gs, chess.D3)  # no capture target -> illegal
            await pilot.pause()
            assert gs.game.board.turn == chess.WHITE
            assert gs.game.board.piece_at(chess.E2) is not None
            assert gs.selected_square is None

    _run_async(_run())


def test_game_legal_move_updates_history():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            _sel(gs, chess.E2)
            await pilot.pause()
            _sel(gs, chess.E4)
            await pilot.pause()
            table = gs.query_one(MoveHistory).query_one(DataTable)
            assert table.get_row_at(0) == ["1", "e4", ""]

    _run_async(_run())


def test_game_promotion_becomes_queen():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            gs.game.board = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
            _sel(gs, chess.A7)
            await pilot.pause()
            _sel(gs, chess.A8)
            await pilot.pause()
            piece = gs.game.board.piece_at(chess.A8)
            assert piece is not None
            assert piece.piece_type == chess.QUEEN

    _run_async(_run())


def test_game_on_engine_finished_updates_eval_and_history():
    async def _run():
        app = _Host()
        async with app.run_test(size=(140, 45)) as pilot:
            app.push_screen(GameScreen(elo=1500, player_color=chess.WHITE))
            await pilot.pause()
            gs = cast(GameScreen, app.screen)
            gs.on_engine_finished("e5", 0.5)
            await pilot.pause()
            assert gs.query_one(EvalMeter).score == 0.5
            table = gs.query_one(MoveHistory).query_one(DataTable)
            assert table.get_row_at(0) == ["1", "e5", ""]

    _run_async(_run())
