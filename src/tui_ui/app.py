"""app.py: Full Textual Application wiring together all components."""

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Log, Button
import chess

from core.game import Game
from engine.stonk_engine import StonkEngine
from tui_ui.widgets.board import ChessBoardGrid, ChessSquare
from tui_ui.widgets.eval_meter import EvalMeter
from tui_ui.widgets.input import MoveInputBar
from tui_ui.widgets.move_history import MoveHistory


class StonkfishTUI(App):
    """The complete Stonkfish Chess Textual TUI."""

    TITLE = "Stonkfish Chess"

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }

    #main_container {
        height: 1fr;
        width: 100%;
    }

    #left_pane {
        width: 36;
        height: 100%;
    }

    #right_pane {
        width: 1fr;
        height: 100%;
    }

    #board_container {
        height: 18;
        width: 34;
        content-align: center middle;
    }

    #log {
        height: 1fr;
        border: solid green;
    }

    #bottom_bar {
        height: 3;
        width: 100%;
        padding: 0 1;
    }

    #input_bar {
        width: 1fr;
    }

    #btn_quit {
        width: 12;
        margin-left: 1;
    }
    """

    def __init__(self, elo: int = 1500, player_color: chess.Color = chess.WHITE):
        super().__init__()
        self.game = Game()
        self.engine = None
        self.elo = elo
        self.player_color = player_color
        self.selected_square = None

    def compose(self) -> ComposeResult:
        yield Header()

        # Split screen into main game area and bottom control bar
        with Horizontal(id="main_container"):
            # Left pane: Eval meter & Board
            with Vertical(id="left_pane"):
                yield EvalMeter(id="eval_meter")
                with Container(id="board_container"):
                    yield ChessBoardGrid(invert=(self.player_color == chess.BLACK), id="board")

            # Right pane: Move history & event log
            with Vertical(id="right_pane"):
                yield MoveHistory(id="move_history")
                yield Log(id="log")

        # Bottom Bar: Input field + Mouse-clickable Quit button
        with Horizontal(id="bottom_bar"):
            yield MoveInputBar(id="input_bar")
            yield Button("Quit", id="btn_quit", variant="error")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize engine and sync initial board state."""
        log = self.query_one(Log)
        try:
            self.engine = StonkEngine()
            self.engine.configure_elo(self.elo)
            log.write_line(f"StonkEngine initialized (Elo: {self.elo}).")
        except FileNotFoundError as e:
            log.write_line(f"Engine setup failed: {e}")

        # Render initial board
        board_widget = self.query_one(ChessBoardGrid)
        board_widget.update_board(self.game.board)

    # --- INPUT HANDLERS ---

    def on_move_input_bar_move_submitted(self, message: MoveInputBar.MoveSubmitted) -> None:
        """Handle moves typed via MoveInputBar."""
        san = message.command
        if san.lower() in ["quit", "exit"]:
            self.exit(result="quit")
            return

        self.attempt_player_move(san)

    def on_chess_square_square_selected(self, message: ChessSquare.SquareSelected) -> None:
        """Handle click-to-move via mouse selection."""
        sq = message.square_index
        board_widget = self.query_one(ChessBoardGrid)

        if self.selected_square is None:
            # First click: Select source piece
            piece = self.game.board.piece_at(sq)
            if piece and piece.color == self.game.board.turn:
                self.selected_square = sq
                board_widget.highlight_square(sq)
        else:
            # Second click: Attempt destination move
            move = chess.Move(self.selected_square, sq)

            # Check promotion default (queen)
            piece = self.game.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN and chess.square_rank(sq) in (0, 7):
                move.promotion = chess.QUEEN

            if move in self.game.board.legal_moves:
                san = self.game.board.san(move)
                self.attempt_player_move(san)

            self.selected_square = None
            board_widget.highlight_square(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Mouse click on Quit button."""
        if event.button.id == "btn_quit":
            self.exit(result="quit")

    # --- GAME & ENGINE LOGIC ---

    def attempt_player_move(self, san_move: str) -> None:
        """Validate player move and trigger engine response if valid."""
        log = self.query_one(Log)

        if self.game.make_player_move(san_move):
            log.write_line(f"You played: {san_move}")
            self.sync_board_and_history(san_move)

            # Trigger engine turn in worker thread
            if not self.game.is_over():
                self.trigger_engine_turn()
        else:
            log.write_line(f"Illegal move: '{san_move}'")

    @work(exclusive=True, thread=True)
    def trigger_engine_turn(self) -> None:
        """Worker thread to run engine calculation without blocking UI thread."""
        log = self.query_one(Log)
        log.write_line("Stonkfish thinking...")

        if self.engine:
            engine_move = self.engine.get_best_move(self.game.board, time_limit=0.5)
            played_san = self.game.make_engine_move(engine_move)
        else:
            log.write_line("Engine not configured.")
            return

        # Update UI back on main thread
        self.call_from_thread(self.on_engine_finished, played_san)

    def on_engine_finished(self, played_san: str) -> None:
        """Executed on main loop after engine completes calculation."""
        log = self.query_one(Log)
        log.write_line(f"Stonkfish played: {played_san}")
        self.sync_board_and_history(played_san)

    def sync_board_and_history(self, san_move: str) -> None:
        """Synchronize updated board state across widgets."""
        self.query_one(ChessBoardGrid).update_board(self.game.board)
        self.query_one(MoveHistory).add_move(san_move)

        if self.game.is_over():
            self.query_one(Log).write_line(f"Game Over! Result: {self.game.get_result()}")