import chess
import chess.engine
import os

# Start the Stockfish executable process
script_dir = os.path.dirname(os.path.abspath(__file__))
stockfish_path = os.path.join(script_dir, "..", "bin", "stockfish")
engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

board = chess.Board()

# Ask Stockfish to evaluate the position for 0.1 seconds
result = engine.analyse(board, chess.engine.Limit(time=0.1))
score = result.get("score")
if score:
    print("Evaluation:", score.white())
else:
    print("Evaluation:", score)

# Ask Stockfish to pick the best move
best_move = engine.play(board, chess.engine.Limit(depth=15))
print("Best move:", best_move.move)

engine.quit()