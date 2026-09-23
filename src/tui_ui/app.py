"""Full Textual application with a setup screen and game view."""

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Header, Footer, Log, Button, Input, RadioSet, RadioButton, Label
import chess

from core.game import Game
from engine.stonk_engine import StonkEngine
from tui_ui.widgets.board import ChessBoardGrid, ChessSquare
from tui_ui.widgets.eval_meter import EvalMeter
from tui_ui.widgets.input import MoveInputBar
from tui_ui.widgets.move_history import MoveHistory


class SetupScreen(ModalScreen):
    """Modal screen shown on launch to configure Elo and Color."""

    CSS = """
    SetupScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #dialog {
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        width: 50;
        height: auto;
    }

    .field-title {
        margin-top: 1;
        text-style: bold;
    }

    #elo_input {
        margin-bottom: 1;
    }

    #button_bar {
        margin-top: 1;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("=== Stonkfish Game Setup ===", id="title")

            yield Label("Engine Elo (1320 - 2800):", classes="field-title")
            yield Input(value="1500", placeholder="1500", id="elo_input")

            yield Label("Select Your Color:", classes="field-title")
            with RadioSet(id="color_select"):
                yield RadioButton("White", value=True, id="radio_white")
                yield RadioButton("Black", id="radio_black")

            with Horizontal(id="button_bar"):
                yield Button("Start Game", id="btn_start", variant="success")
                yield Button("Quit", id="btn_quit", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_quit":
            self.app.exit()
            return

        if event.button.id == "btn_start":
            elo_val = self.query_one("#elo_input", Input).value.strip()
            if not elo_val.isdigit() or not (1320 <= int(elo_val) <= 2800):
                self.notify("Elo must be an integer between 1320 and 2800", severity="error")
                return

            elo = int(elo_val)
            is_white = self.query_one("#radio_white", RadioButton).value
            player_color = chess.WHITE if is_white else chess.BLACK

            self.dismiss((elo, player_color))


class GameScreen(Screen):
    """Main Chess Game Screen."""

    CSS = """
    GameScreen {
        layout: vertical;
    }

    #main_container {
        height: 1fr;
        width: 100%;
    }

    #left_pane {
        width: 44;
        height: 100%;
        align: center top;
    }

    #right_pane {
        width: 1fr;
        height: 100%;
    }

    #board_container {
        height: auto;
        width: auto;
        content-align: center middle;
    }

    #move_history {
        height: 10;
        border: solid blue;
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

    def __init__(self, elo: int, player_color: chess.Color):
        super().__init__()
        self.elo = elo
        self.player_color = player_color
        self.game = Game()
        self.engine = None
        self.selected_square = None

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main_container"):
            with Vertical(id="left_pane"):
                yield EvalMeter(id="eval_meter")
                with Container(id="board_container"):
                    yield ChessBoardGrid(invert=(self.player_color == chess.BLACK), id="board")

            with Vertical(id="right_pane"):
                yield MoveHistory(id="move_history")
                yield Log(id="log")

        with Horizontal(id="bottom_bar"):
            yield MoveInputBar(id="input_bar")
            yield Button("Quit", id="btn_quit", variant="error")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize engine, sync board state, and set focus to the board."""
        log = self.query_one(Log)
        try:
            self.engine = StonkEngine()
            self.engine.configure_elo(self.elo)
            log.write_line(f"Stonkfish ready (Elo: {self.elo}). Playing as {'White' if self.player_color == chess.WHITE else 'Black'}.")
        except FileNotFoundError as e:
            log.write_line(f"Engine setup failed: {e}")

        # Update board display
        board_widget = self.query_one(ChessBoardGrid)
        board_widget.update_board(self.game.board)

        # Focus the chessboard grid immediately for keyboard control
        board_widget.focus()

        if self.player_color == chess.BLACK:
            self.trigger_engine_turn()

    # --- INPUT HANDLERS ---

    def on_chess_board_grid_selection_cancelled(self, message: ChessBoardGrid.SelectionCancelled) -> None:
        """Handle ESC key press to clear square selection."""
        self.selected_square = None
        self.query_one(ChessBoardGrid).highlight_square(None)

    def on_move_input_bar_move_submitted(self, message: MoveInputBar.MoveSubmitted) -> None:
        san = message.command
        if san.lower() in ["quit", "exit"]:
            self.app.exit()
            return
        self.attempt_player_move(san)

    def on_chess_square_square_selected(self, message: ChessSquare.SquareSelected) -> None:
        sq = message.square_index
        board_widget = self.query_one(ChessBoardGrid)

        if self.selected_square is None:
            piece = self.game.board.piece_at(sq)
            if piece and piece.color == self.game.board.turn:
                self.selected_square = sq
                board_widget.highlight_square(sq)
        else:
            move = chess.Move(self.selected_square, sq)
            piece = self.game.board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN and chess.square_rank(sq) in (0, 7):
                move.promotion = chess.QUEEN

            if move in self.game.board.legal_moves:
                san = self.game.board.san(move)
                self.attempt_player_move(san)

            self.selected_square = None
            board_widget.highlight_square(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_quit":
            self.app.exit()

    # --- GAME & ENGINE LOGIC ---

    def attempt_player_move(self, san_move: str) -> None:
        log = self.query_one(Log)

        if self.game.make_player_move(san_move):
            log.write_line(f"You played: {san_move}")
            self.sync_board_and_history(san_move)

            if not self.game.is_over():
                self.trigger_engine_turn()
        else:
            log.write_line(f"Illegal move: '{san_move}'")

    @work(exclusive=True, thread=True)
    def trigger_engine_turn(self) -> None:
        log = self.query_one(Log)
        log.write_line("Stonkfish thinking...")

        if self.engine:
            engine_move, eval_score = self.engine.get_best_move_and_eval(self.game.board, time_limit=0.5)
            played_san = self.game.make_engine_move(engine_move)
        else:
            log.write_line("Engine not configured.")
            return

        self.app.call_from_thread(self.on_engine_finished, played_san, eval_score)

    def on_engine_finished(self, played_san: str, eval_score: float) -> None:
        log = self.query_one(Log)
        log.write_line(f"Stonkfish played: {played_san} (Eval: {eval_score:+.2f})")

        self.sync_board_and_history(played_san)
        self.query_one(EvalMeter).update_eval(eval_score)

    def sync_board_and_history(self, san_move: str) -> None:
        self.query_one(ChessBoardGrid).update_board(self.game.board)
        self.query_one(MoveHistory).add_move(san_move)

        if self.game.is_over():
            self.query_one(Log).write_line(f"Game Over! Result: {self.game.get_result()}")


class StonkfishTUI(App):
    """The complete Stonkfish Chess Textual TUI."""

    TITLE = "Stonkfish Chess"
    BINDINGS = [("q", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen(SetupScreen(), self.on_setup_completed)

    def on_setup_completed(self, setup_data: tuple[int, chess.Color] | None) -> None:
        if setup_data is None:
            self.exit()
            return

        elo, player_color = setup_data
        self.push_screen(GameScreen(elo=elo, player_color=player_color))