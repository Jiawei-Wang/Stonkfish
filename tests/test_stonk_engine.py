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


def test_missing_binary_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        StonkEngine(binary_path="/nonexistent/stockfish_xyz")


_SKIP_NO_BINARY = pytest.mark.skipif(
    not _binary_available(),
    reason="Stockfish binary (bin/stockfish or stockfish on PATH) is not present",
)

_MATED = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"


@_SKIP_NO_BINARY
def test_default_binary_path_resolves():
    engine = StonkEngine()
    try:
        assert os.path.exists(engine.path)
    finally:
        engine.quit()


@_SKIP_NO_BINARY
def test_configure_elo_does_not_raise():
    engine = StonkEngine()
    try:
        engine.configure_elo(1500)
    finally:
        engine.quit()


@_SKIP_NO_BINARY
def test_get_best_move_and_eval_returns_move_and_float():
    engine = StonkEngine()
    try:
        move, eval_score = engine.get_best_move_and_eval(chess.Board(), time_limit=0.3)
        assert isinstance(move, chess.Move)
        assert isinstance(eval_score, float)
    finally:
        engine.quit()


@_SKIP_NO_BINARY
def test_get_best_move_and_eval_raises_when_no_legal_moves():
    engine = StonkEngine()
    try:
        with pytest.raises(RuntimeError):
            engine.get_best_move_and_eval(chess.Board(_MATED), time_limit=0.3)
    finally:
        engine.quit()


@_SKIP_NO_BINARY
def test_get_best_move_and_eval_accumulates_think_time():
    engine = StonkEngine()
    try:
        assert engine.total_think_time == 0.0
        engine.get_best_move_and_eval(chess.Board(), time_limit=0.3)
        assert engine.total_think_time == pytest.approx(0.3)
    finally:
        engine.quit()


@_SKIP_NO_BINARY
def test_configure_elo_updates_current_elo():
    engine = StonkEngine()
    try:
        assert engine.current_elo is None
        engine.configure_elo(1500)
        assert engine.current_elo == 1500
    finally:
        engine.quit()



