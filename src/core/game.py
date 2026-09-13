import chess

"""
Manage board state, validate incoming SAN move inputs, and map moves between engine UCI outputs and player SAN representations.
"""
class Game:
    def __init__(self):
        self.board = chess.Board()

    def make_player_move(self, san_move_str: str) -> bool:
        """Parses and plays a SAN move (e.g. e4, Nf3, O-O). Returns True if valid."""
        try:
            move = self.board.parse_san(san_move_str.strip())
            self.board.push(move)
            return True
        except ValueError:
            return False

    def make_engine_move(self, move: chess.Move) -> str:
        """Converts an engine Move object to SAN for printing, then pushes it."""
        san_str = self.board.san(move)
        self.board.push(move)
        return san_str

    def is_over(self) -> bool:
        return self.board.is_game_over()

    def get_result(self) -> str:
        return self.board.result()