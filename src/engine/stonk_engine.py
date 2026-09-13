import os
import chess
import chess.engine

"""
stockfish wrapper
Encapsulate Stockfish initialization, option configuration (Elo ratings, search time/depth), and move analysis.
"""
class StonkEngine:
    def __init__(self, binary_path: str | None = None):
        if binary_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            binary_path = os.path.join(base_dir, "..", "..", "bin", "stockfish")

        self.path = binary_path
        self.engine = chess.engine.SimpleEngine.popen_uci(self.path)

    def configure_elo(self, elo: int):
        """Sets engine playing strength using standard UCI limits."""
        self.engine.configure({
            "UCI_LimitStrength": True,
            "UCI_Elo": elo,
        })

    def get_best_move(self, board: chess.Board, time_limit: float = 0.5) -> chess.Move:
        """Requests the best move from Stockfish for the given board state."""
        result = self.engine.play(board, chess.engine.Limit(time=time_limit))
        
        if result.move is None:
            raise RuntimeError("Engine failed to return a move.")
            
        return result.move

    def quit(self):
        self.engine.quit()