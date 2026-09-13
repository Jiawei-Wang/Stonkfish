import chess

"""
Render the chess board with Unicode symbols, board coordinates, and empty square accents.
"""

UNICODE_PIECES = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    '.': '.'
}

def render_board(board: chess.Board, invert: bool = False) -> str:
    """Returns a formatted Unicode string representation of the board."""
    lines = []
    lines.append("  a b c d e f g h")
    
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
        
    lines.append("  a b c d e f g h")
    return "\n".join(lines)