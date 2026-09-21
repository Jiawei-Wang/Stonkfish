import chess

from core.game import Game


def test_make_player_move_legal_returns_true_and_pushes():
    game = Game()
    assert game.make_player_move("e4") is True
    piece = game.board.piece_at(chess.E4)
    assert piece is not None
    assert piece.symbol() == "P"
    assert game.board.turn == chess.BLACK


def test_make_player_move_illegal_for_side_to_move_returns_false():
    game = Game()
    assert game.make_player_move("e4") is True
    assert game.make_player_move("e4") is False


def test_make_player_move_invalid_san_returns_false():
    game = Game()
    assert game.make_player_move("z9") is False
    assert game.make_player_move("") is False
    assert game.make_player_move("e22") is False


def test_make_player_move_strips_whitespace():
    game = Game()
    assert game.make_player_move("  e4  ") is True
    assert game.board.turn == chess.BLACK


def test_make_engine_move_returns_san_and_pushes():
    game = Game()
    game.board.push(game.board.parse_uci("e2e4"))
    move = game.board.parse_uci("e7e5")
    assert game.make_engine_move(move) == "e5"
    piece = game.board.piece_at(chess.E5)
    assert piece is not None
    assert piece.symbol() == "p"
    assert game.board.turn == chess.WHITE


def test_is_over_false_initial():
    assert Game().is_over() is False


def test_is_over_true_on_checkmate():
    game = Game()
    game.board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    assert game.is_over() is True


def test_is_over_true_on_draw():
    game = Game()
    game.board = chess.Board("8/8/8/8/8/8/K7/k7 w - - 0 1")
    assert game.is_over() is True


def test_get_result_checkmate():
    game = Game()
    game.board = chess.Board("r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4")
    assert game.get_result() == "1-0"


def test_get_result_running_game_is_star():
    assert Game().get_result() == "*"


def test_get_result_draw_is_half_point():
    game = Game()
    game.board = chess.Board("8/8/8/8/8/8/K7/k7 w - - 0 1")
    assert game.get_result() == "1/2-1/2"


def test_make_player_move_castling():
    game = Game()
    game.board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert game.make_player_move("O-O") is True
    # Kingside castle: king e1->g1, rook h1->f1.
    assert game.board.piece_at(chess.G1) is not None
    assert game.board.piece_at(chess.G1).symbol() == "K"
    assert game.board.piece_at(chess.F1) is not None
    assert game.board.piece_at(chess.F1).symbol() == "R"


def test_make_player_move_promotion():
    game = Game()
    game.board = chess.Board("8/P3k3/8/8/8/8/8/4K3 w - - 0 1")
    assert game.make_player_move("a8=Q") is True
    assert game.board.piece_at(chess.A8) is not None
    assert game.board.piece_at(chess.A8).symbol() == "Q"


def test_make_engine_move_castling_san():
    game = Game()
    game.board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1")
    move = game.board.parse_uci("e8g8")
    assert game.make_engine_move(move) == "O-O"


def test_make_engine_move_promotion_san():
    game = Game()
    game.board = chess.Board("8/P3k3/8/8/8/8/8/4K3 w - - 0 1")
    move = game.board.parse_uci("a7a8q")
    assert game.make_engine_move(move) == "a8=Q"


def test_make_player_move_into_checkmate():
    game = Game()
    game.board = chess.Board("7k/5ppp/8/8/8/8/5PPP/R6K w - - 0 1")
    assert game.make_player_move("Ra8#") is True
    assert game.is_over() is True
    assert game.get_result() == "1-0"
