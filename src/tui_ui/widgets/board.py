"""board.py: Interactive 8x8 Chess Board Grid Widget for Textual."""

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static
import chess

# Standard Unicode representations for chess pieces
UNICODE_PIECES = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    '.': ' '
}


class ChessSquare(Static):
    """Widget representing a single square on the chess board."""

    DEFAULT_CSS = """
    ChessSquare {
        width: 4;
        height: 2;
        content-align: center middle;
        text-style: bold;
    }
    ChessSquare.light-square {
        background: #f0d9b5;
        color: #111111;
    }
    ChessSquare.dark-square {
        background: #b58863;
        color: #111111;
    }
    ChessSquare.selected {
        background: #769656;  /* Highlight color for clicked square */
        color: #ffffff;
    }
    ChessSquare.last-move {
        background: #baca44;  /* Highlight for last move made */
    }
    """

    class SquareSelected(Message):
        """Custom event emitted when a square is clicked."""
        def __init__(self, square_index: int) -> None:
            super().__init__()
            self.square_index = square_index

    def __init__(self, square_index: int, piece_symbol: str = "."):
        super().__init__(UNICODE_PIECES.get(piece_symbol, " "))
        self.square_index = square_index

        # Apply default background based on board rank/file parity
        rank = chess.square_rank(square_index)
        file = chess.square_file(square_index)
        is_light = (rank + file) % 2 != 0
        self.add_class("light-square" if is_light else "dark-square")

    def set_piece(self, piece_symbol: str) -> None:
        """Update the piece display on this square."""
        symbol = UNICODE_PIECES.get(piece_symbol, " ")
        self.update(symbol)

    def on_click(self) -> None:
        """Post a selection message whenever the user clicks this square."""
        self.post_message(self.SquareSelected(self.square_index))


class ChessBoardGrid(Widget):
    """Widget rendering an 8x8 interactive chess board."""

    DEFAULT_CSS = """
    ChessBoardGrid {
        layout: grid;
        grid-size: 8 8;
        width: 32;
        height: 16;
        border: solid green;
    }
    """

    def __init__(self, invert: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.invert = invert
        self.selected_square: int | None = None

    def compose(self) -> ComposeResult:
        """Yield 64 square widgets ordered by rank and file."""
        # Standard white perspective: Rank 7 down to 0, File 0 to 7
        # Black perspective: Rank 0 up to 7, File 7 down to 0
        rank_range = range(0, 8) if self.invert else range(7, -1, -1)
        file_range = range(7, -1, -1) if self.invert else range(0, 8)

        for rank in rank_range:
            for file in file_range:
                sq_idx = chess.square(file, rank)
                yield ChessSquare(square_index=sq_idx)

    def update_board(self, board: chess.Board) -> None:
        """Sync square contents with a python-chess Board object."""
        for square_widget in self.query(ChessSquare):
            sq_idx = square_widget.square_index
            piece = board.piece_at(sq_idx)
            symbol = piece.symbol() if piece else "."
            square_widget.set_piece(symbol)

    def highlight_square(self, square_index: int | None) -> None:
        """Highlight a clicked/selected square, clearing previous selection."""
        # Clear previous highlights
        for sq in self.query(ChessSquare):
            sq.remove_class("selected")

        if square_index is not None:
            self.selected_square = square_index
            for sq in self.query(ChessSquare):
                if sq.square_index == square_index:
                    sq.add_class("selected")