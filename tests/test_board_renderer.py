import chess

from ui.board_renderer import UNICODE_PIECES, render_board


def test_initial_board_shape_and_headers():
    out = render_board(chess.Board())
    lines = out.splitlines()
    assert len(lines) == 10
    assert lines[0] == "  a b c d e f g h"
    assert lines[-1] == "  a b c d e f g h"


def test_initial_board_contains_all_piece_unicode_symbols():
    out = render_board(chess.Board())
    for glyph in ("♔", "♕", "♖", "♗", "♘", "♙"):
        assert glyph in out


def test_top_line_is_rank8_in_normal_orientation():
    out = render_board(chess.Board())
    assert out.splitlines()[1].startswith("8 ")


def test_top_line_is_rank1_when_inverted():
    out = render_board(chess.Board(), invert=True)
    assert out.splitlines()[1].startswith("1 ")


def test_piece_symbol_map_defaults():
    assert UNICODE_PIECES["k"] == "♚"
    assert UNICODE_PIECES["."] == "."
