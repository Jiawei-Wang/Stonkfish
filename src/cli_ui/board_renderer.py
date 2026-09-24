"""Render a chess board as a printable Unicode string.

Produces a text board with Unicode piece symbols, file/rank coordinates on
all four edges, and a dot for empty squares. Optionally flips orientation so
the board can be shown from either player's perspective.
"""

import chess

# Maps each piece symbol (uppercase = white, lowercase = black) to its
# Unicode glyph.
UNICODE_PIECES = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    '.': '.'
}


def render_board(board: chess.Board, invert: bool = False) -> str:
    """Return a formatted Unicode string representation of the board.

    Args:
        board: The board position to render.
        invert: When True, flip the orientation so rank 1 is on top and the
            files run right-to-left (i.e. view from Black's perspective).

    Returns:
        str: The board as a multi-line string with coordinate labels.
    """



    lines = []
    lines.append("  a b c d e f g h") if not invert else lines.append("  h g f e d c b a")  # Flip orientation for Black's perspective

    # Inverting reverses both axes so the board is viewed from the opposite
    # side.
    ranks = range(8) if invert else range(7, -1, -1)
    files = range(7, -1, -1) if invert else range(8)

    for rank in ranks:
        row_str = f"{rank + 1} "
        for file in files:
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            symbol = UNICODE_PIECES[piece.symbol()] if piece else '.'
            row_str += f"{symbol} "
        row_str += f"{rank + 1}"
        lines.append(row_str)

    lines.append("  a b c d e f g h") if not invert else lines.append("  h g f e d c b a")  # Flip orientation for Black's perspective
    return "\n".join(lines)
