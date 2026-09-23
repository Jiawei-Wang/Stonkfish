"""Tests for the Textual chess board widgets (ChessSquare, ChessBoardGrid)."""

import asyncio

import chess

from textual.app import App, ComposeResult

from tui_ui.widgets.board import ChessBoardGrid, ChessSquare


def _rgb(color) -> tuple[int, int, int]:
    return (color.r, color.g, color.b)


def _run_async(coro):
    asyncio.run(coro)


# --- ChessSquare (pure, no app needed) ---


def test_square_a1_is_dark():
    assert ChessSquare(square_index=chess.A1).is_light is False


def test_square_b1_is_light():
    assert ChessSquare(square_index=chess.B1).is_light is True


def test_square_default_renders_blank():
    assert ChessSquare(square_index=chess.E4).render().plain == " "


def test_square_set_piece_updates_glyph():
    sq = ChessSquare(square_index=chess.E2)
    sq.set_piece("P")
    assert sq.render().plain == "♙"
    sq.set_piece("p")
    assert sq.render().plain == "♟"
    sq.set_piece(".")
    assert sq.render().plain == " "


def test_square_set_state_selected():
    sq = ChessSquare(square_index=chess.A1)
    sq.set_state(is_selected=True, is_cursor=False)
    assert _rgb(sq.styles.background) == (0x76, 0x96, 0x56)
    assert _rgb(sq.styles.color) == (0xFF, 0xFF, 0xFF)


def test_square_set_state_cursor():
    sq = ChessSquare(square_index=chess.A1)
    sq.set_state(is_selected=False, is_cursor=True)
    assert _rgb(sq.styles.background) == (0xBA, 0xCA, 0x44)
    assert _rgb(sq.styles.color) == (0x11, 0x11, 0x11)


def test_square_set_state_normal_light():
    sq = ChessSquare(square_index=chess.B1)
    sq.set_state(is_selected=False, is_cursor=False)
    assert _rgb(sq.styles.background) == (0xF0, 0xD9, 0xB5)


def test_square_set_state_normal_dark():
    sq = ChessSquare(square_index=chess.A1)
    sq.set_state(is_selected=False, is_cursor=False)
    assert _rgb(sq.styles.background) == (0xB5, 0x88, 0x63)


def test_square_selected_takes_precedence_over_cursor():
    sq = ChessSquare(square_index=chess.A1)
    sq.set_state(is_selected=True, is_cursor=True)
    assert _rgb(sq.styles.background) == (0x76, 0x96, 0x56)


# --- ChessBoardGrid: pure logic (no app needed) ---


def test_grid_cursor_starts_on_e4():
    assert ChessBoardGrid().cursor_square == chess.E4


def test_grid_compose_yields_64_squares():
    assert len(list(ChessBoardGrid().compose())) == 64


def test_grid_compose_normal_first_is_a8():
    first = list(ChessBoardGrid().compose())[0]
    assert first.square_index == chess.A8


def test_grid_compose_invert_first_is_h1():
    first = list(ChessBoardGrid(invert=True).compose())[0]
    assert first.square_index == chess.H1


def test_grid_move_cursor_up():
    g = ChessBoardGrid()
    g.action_move_cursor("up")
    assert g.cursor_square == chess.E5


def test_grid_move_cursor_down():
    g = ChessBoardGrid()
    g.action_move_cursor("down")
    assert g.cursor_square == chess.E3


def test_grid_move_cursor_left():
    g = ChessBoardGrid()
    g.action_move_cursor("left")
    assert g.cursor_square == chess.D4


def test_grid_move_cursor_right():
    g = ChessBoardGrid()
    g.action_move_cursor("right")
    assert g.cursor_square == chess.F4


def test_grid_move_cursor_clamps_at_top():
    g = ChessBoardGrid()
    g.cursor_square = chess.A8
    g.action_move_cursor("up")
    assert g.cursor_square == chess.A8


def test_grid_move_cursor_clamps_at_left():
    g = ChessBoardGrid()
    g.cursor_square = chess.A8
    g.action_move_cursor("left")
    assert g.cursor_square == chess.A8


def test_grid_move_cursor_invert_up_decreases_rank():
    g = ChessBoardGrid(invert=True)
    g.action_move_cursor("up")
    assert g.cursor_square == chess.E3


def test_grid_move_cursor_invert_left_increases_file():
    g = ChessBoardGrid(invert=True)
    g.action_move_cursor("left")
    assert g.cursor_square == chess.F4


def test_grid_highlight_square_sets_selected():
    g = ChessBoardGrid()
    g.highlight_square(chess.D4)
    assert g.selected_square == chess.D4
    g.highlight_square(None)
    assert g.selected_square is None


# --- ChessBoardGrid: needs a mounted app ---


class _BoardApp(App):
    def __init__(self, invert: bool = False):
        super().__init__()
        self.invert = invert
        self.cancelled = 0
        self.selected: list[chess.square] = []

    def compose(self) -> ComposeResult:
        yield ChessBoardGrid(invert=self.invert, id="board")

    def on_chess_board_grid_selection_cancelled(self, message):
        self.cancelled += 1

    def on_chess_square_square_selected(self, message):
        self.selected.append(message.square_index)


def test_grid_update_board_syncs_pieces():
    async def _run():
        app = _BoardApp()
        async with app.run_test() as pilot:
            grid = app.query_one(ChessBoardGrid)
            grid.update_board(chess.Board())
            e2 = next(sq for sq in grid.query(ChessSquare) if sq.square_index == chess.E2)
            assert e2.render().plain == "♙"
            e5 = next(sq for sq in grid.query(ChessSquare) if sq.square_index == chess.E5)
            assert e5.render().plain == " "

    _run_async(_run())


def test_grid_enter_posts_square_selected():
    async def _run():
        app = _BoardApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("enter")
            assert app.selected == [chess.E4]

    _run_async(_run())


def test_grid_escape_posts_selection_cancelled():
    async def _run():
        app = _BoardApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("escape")
            assert app.cancelled == 1

    _run_async(_run())


def test_grid_arrow_key_moves_cursor():
    async def _run():
        app = _BoardApp()
        async with app.run_test() as pilot:
            grid = app.query_one(ChessBoardGrid)
            await pilot.pause()
            await pilot.press("up")
            assert grid.cursor_square == chess.E5

    _run_async(_run())
