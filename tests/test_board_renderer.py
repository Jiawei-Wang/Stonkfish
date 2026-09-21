import chess

from cli_ui.board_renderer import UNICODE_PIECES, render_board


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


def test_all_files_rendered_in_order_normal():
    out = render_board(chess.Board())
    # Rank 8 row: black pieces, files a..h left to right.
    rank8 = out.splitlines()[1]
    assert rank8.startswith("8 ")
    assert rank8.endswith(" 8")
    # The eight square cells appear in file order a..h.
    assert "♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜" in rank8


def test_inverted_reverses_file_order():
    out = render_board(chess.Board(), invert=True)
    # Viewed from Black's side, rank 1 is on top and files run h..a, so the
    # king and queen swap columns compared to the normal orientation.
    top = out.splitlines()[1]
    assert top.startswith("1 ")
    assert "♖ ♘ ♗ ♔ ♕ ♗ ♘ ♖" in top


def test_empty_square_renders_as_dot():
    board = chess.Board("8/8/8/8/8/8/8/8 w - - 0 1")
    out = render_board(board)
    # Every one of the 64 squares is empty.
    assert out.count(".") >= 64


def test_single_piece_position():
    board = chess.Board("8/8/8/8/8/8/8/4K3 w - - 0 1")
    out = render_board(board)
    lines = out.splitlines()
    # White king on e1 -> bottom row (rank 1), file e (5th cell).
    assert "♔" in lines[8]
    assert lines[8].split()[5] == "♔"
