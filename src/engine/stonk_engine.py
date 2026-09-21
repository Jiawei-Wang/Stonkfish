"""Engine integration module for Stonkfish.

Wraps the local Stockfish binary via python-chess UCI protocol, managing engine
lifecycle, skill level configuration, and best-move analysis.
"""

import os
import chess
import chess.engine


class StonkEngine:
    """Manages low-level UCI communication and move generation with Stockfish.

    Encapsulates binary process startup, UCI option configuration (e.g. Elo
    rating), and synchronous move selection.
    """

    def __init__(self, binary_path: str | None = None):
        """Initializes the Stockfish engine process.

        Args:
            binary_path: Path to the executable. Defaults to bin/stockfish
                relative to project root if unspecified.

        Raises:
            FileNotFoundError: If no executable exists at the target path.
        """

        # --- Internal State ---

        # Resolved filesystem path to the Stockfish executable binary.
        self.path: str = binary_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "bin", "stockfish",
        )

        if not os.path.isfile(self.path):
            raise FileNotFoundError(
                f"Stockfish binary not found at {self.path}. "
                "Place it at bin/stockfish or add stockfish to your PATH."
            )

        # Active UCI subprocess handler from python-chess.
        self.engine: chess.engine.SimpleEngine = (
            chess.engine.SimpleEngine.popen_uci(self.path)
        )

        # Configured playing strength (Elo); None indicates unrestricted
        # strength.
        self.current_elo: int | None = None

        # Cumulative search time spent across all moves in seconds.
        self.total_think_time: float = 0.0

    def configure_elo(self, elo: int) -> None:
        """Sets engine playing strength using standard UCI limits.

        Args:
            elo: Target rating bounded between 1320 and 2800.
        """
        self.engine.configure({
            "UCI_LimitStrength": True,
            "UCI_Elo": elo,
        })
        self.current_elo = elo


    def get_best_move_and_eval(
        self, board: chess.Board, time_limit: float = 0.5
    ) -> tuple[chess.Move, float]:
        """Request the best move from Stockfish for the given board position.

        Args:
            board: Current python-chess Board state.
            time_limit: Maximum search time allowed in seconds.

        Returns:
            tuple[chess.Move, float]: The engine's chosen move and the
            evaluation score in pawns from White's perspective.

        Raises:
            RuntimeError: If the engine fails to produce a valid move.
        """
        result = self.engine.play(
            board,
            chess.engine.Limit(time=time_limit),
            info=chess.engine.INFO_SCORE,
        )

        if result.move is None:
            raise RuntimeError("Engine failed to return a move.")

        score = result.info.get("score")
        if score is not None:
            centipawns = score.white().score(mate_score=10000)
            eval_score = centipawns / 100.0
        else:
            eval_score = 0.0

        self.total_think_time += time_limit
        return result.move, eval_score

    def quit(self) -> None:
        """Terminate the background Stockfish subprocess."""
        self.engine.quit()