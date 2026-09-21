"""Board state management and move handling for a Stonkfish match.

Wraps a ``chess.Board`` and provides the operations the app needs: playing
player moves supplied as SAN, applying engine moves supplied as UCI
``chess.Move`` objects, and querying game-over status and the final result.
"""

import chess


class Game:
    """Holds the board and mediates moves between the player and the engine.

    The board is the single source of truth for the position. Player moves
    arrive as SAN strings and are validated against the board; engine moves
    arrive as ``chess.Move`` objects and are converted to SAN for display.
    """

    def __init__(self):
        """Initialize a new game from the standard starting position."""
        self.board = chess.Board()

    def make_player_move(self, san_move_str: str) -> bool:
        """Parse and play a player move given in SAN (e.g. e4, Nf3, O-O).

        Args:
            san_move_str: The move in Standard Algebraic Notation.

        Returns:
            bool: True if the move was legal and applied, False otherwise.
        """
        try:
            move = self.board.parse_san(san_move_str.strip())
            self.board.push(move)
            return True
        except ValueError:
            return False

    def make_engine_move(self, move: chess.Move) -> str:
        """Apply an engine move to the board and return its SAN for display.

        Args:
            move: The engine's chosen move.

        Returns:
            str: The move rendered in Standard Algebraic Notation.
        """
        san_str = self.board.san(move)
        self.board.push(move)
        return san_str

    def is_over(self) -> bool:
        """Return whether the game has reached a terminal state."""
        return self.board.is_game_over()

    def get_result(self) -> str:
        """Return the game result in standard notation.

        For example '1-0', '0-1', '1/2-1/2', or '*' for a running game.
        """
        return self.board.result()
