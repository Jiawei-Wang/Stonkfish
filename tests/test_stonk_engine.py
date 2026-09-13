import os
import shutil

import chess
import pytest

from engine.stonk_engine import StonkEngine

_PATH = shutil.which("stockfish")
_REPO_BIN = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "bin", "stockfish"
    )
)
_BINARIES = [b for b in (_PATH, _REPO_BIN) if b]


def _binary_available() -> bool:
    return bool(_BINARIES)


pytestmark = pytest.mark.skipif(
    not _binary_available(),
    reason="Stockfish binary (bin/stockfish or stockfish on PATH) is not present",
)

_MATED = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"


def test_default_binary_path_resolves():
    engine = StonkEngine()
    try:
        assert os.path.exists(engine.path)
    finally:
        engine.quit()


def test_configure_elo_does_not_raise():
    engine = StonkEngine()
    try:
        engine.configure_elo(1500)
    finally:
        engine.quit()


def test_get_best_move_returns_chess_move():
    engine = StonkEngine()
    try:
        move = engine.get_best_move(chess.Board(), time_limit=0.3)
        assert isinstance(move, chess.Move)
    finally:
        engine.quit()


def test_get_best_move_raises_when_no_legal_moves():
    engine = StonkEngine()
    try:
        with pytest.raises(RuntimeError):
            engine.get_best_move(chess.Board(_MATED), time_limit=0.3)
    finally:
        engine.quit()
