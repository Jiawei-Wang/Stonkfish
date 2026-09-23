"""Interactive 8x8 chess board grid widget for Textual."""

from textual.app import ComposeResult
from textual.binding import Binding
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
        width: 5;
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
    """

    class SquareSelected(Message):
        """Custom event emitted when a square is clicked or selected via keyboard."""
        def __init__(self, square_index: int) -> None:
            super().__init__()
            self.square_index = square_index

    def __init__(self, square_index: int, piece_symbol: str = "."):
        super().__init__(UNICODE_PIECES.get(piece_symbol, " "))
        self.square_index = square_index

        rank = chess.square_rank(square_index)
        file = chess.square_file(square_index)
        self.is_light = (rank + file) % 2 != 0
        self.add_class("light-square" if self.is_light else "dark-square")

    def set_piece(self, piece_symbol: str) -> None:
        """Update the piece display on this square."""
        symbol = UNICODE_PIECES.get(piece_symbol, " ")
        self.update(symbol)

    def set_state(self, is_selected: bool, is_cursor: bool) -> None:
        """Explicitly set inline colors for selection and active cursor position."""
        if is_selected:
            # Highlight chosen piece in high-contrast chess green
            self.styles.background = "#769656"
            self.styles.color = "#ffffff"
        elif is_cursor:
            # Subtle accent tint for active keyboard cursor position
            self.styles.background = "#baca44"
            self.styles.color = "#111111"
        else:
            # Revert to standard board tile color
            self.styles.background = "#f0d9b5" if self.is_light else "#b58863"
            self.styles.color = "#111111"

    def on_click(self) -> None:
        """Post a selection message whenever the user clicks this square."""
        self.post_message(self.SquareSelected(self.square_index))


class ChessBoardGrid(Widget):
    """Widget rendering an 8x8 interactive chess board."""

    DEFAULT_CSS = """
    ChessBoardGrid {
        layout: grid;
        grid-size: 8 8;
        width: 42;
        height: 18;
        border: solid green;
    }

    ChessBoardGrid:focus {
        border: double $accent;
    }
    """

    can_focus = True

    BINDINGS = [
        Binding("up", "move_cursor('up')", "Up", show=True),
        Binding("down", "move_cursor('down')", "Down", show=True),
        Binding("left", "move_cursor('left')", "Left", show=True),
        Binding("right", "move_cursor('right')", "Right", show=True),
        Binding("enter", "select_cursor", "Select", show=True),
        Binding("space", "select_cursor", "Select", show=False),
        Binding("escape", "cancel_selection", "Cancel", show=True),
    ]

    class SelectionCancelled(Message):
        """Custom event emitted when ESC is pressed to clear selection."""
        pass

    def __init__(self, invert: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.invert = invert
        self.selected_square: int | None = None
        self.cursor_square: int = chess.E4

    def compose(self) -> ComposeResult:
        """Yield 64 square widgets ordered by rank and file."""
        rank_range = range(0, 8) if self.invert else range(7, -1, -1)
        file_range = range(7, -1, -1) if self.invert else range(0, 8)

        for rank in rank_range:
            for file in file_range:
                sq_idx = chess.square(file, rank)
                yield ChessSquare(square_index=sq_idx)

    def on_mount(self) -> None:
        """Apply initial render highlights."""
        self.refresh_square_states()

    def action_move_cursor(self, direction: str) -> None:
        """Move cursor position in rank/file space and update visual highlights."""
        file = chess.square_file(self.cursor_square)
        rank = chess.square_rank(self.cursor_square)

        if direction == "up":
            rank += -1 if self.invert else 1
        elif direction == "down":
            rank += 1 if self.invert else -1
        elif direction == "left":
            file += 1 if self.invert else -1
        elif direction == "right":
            file += -1 if self.invert else 1

        file = max(0, min(7, file))
        rank = max(0, min(7, rank))

        self.cursor_square = chess.square(file, rank)
        self.refresh_square_states()

    def action_select_cursor(self) -> None:
        """Post a SquareSelected event for the square under the cursor."""
        self.post_message(ChessSquare.SquareSelected(self.cursor_square))

    def action_cancel_selection(self) -> None:
        """Post a SelectionCancelled event when ESC is pressed."""
        self.post_message(self.SelectionCancelled())

    def update_board(self, board: chess.Board) -> None:
        """Sync square contents with a python-chess Board object."""
        for square_widget in self.query(ChessSquare):
            sq_idx = square_widget.square_index
            piece = board.piece_at(sq_idx)
            symbol = piece.symbol() if piece else "."
            square_widget.set_piece(symbol)

        self.refresh_square_states()

    def highlight_square(self, square_index: int | None) -> None:
        """Set selected square and update square styles across the board."""
        self.selected_square = square_index
        self.refresh_square_states()

    def refresh_square_states(self) -> None:
        """Rerender visual background state for every square on the board."""
        for sq in self.query(ChessSquare):
            is_selected = (sq.square_index == self.selected_square)
            is_cursor = (sq.square_index == self.cursor_square)
            sq.set_state(is_selected=is_selected, is_cursor=is_cursor)