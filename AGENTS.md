# Stonkfish

Modular Python chess app (CLI + planned TUI/GUI/NNUE). Uses `python-chess` for
rules and a Stockfish binary (`bin/stockfish`) over UCI for move generation.

## Environment

- Package manager: **`uv`** (not pip/a raw venv). Python 3.14 is pinned in `.python-version`.
- Install deps: `uv sync`. The only runtime dep is `chess` (imported as `chess`; pip name `python-chess`).
- `requirements.txt` is **stale/misleading** (`python-chess>=1.999`). Trust `pyproject.toml` + `uv.lock`.

## Running

- Real entrypoint is **`src/main.py`**. Run from repo root: `uv run python src/main.py`.
- Imports in `src/` are **flat** (`from core.game import Game`, not `from src.core...`). They resolve because Python puts the script's directory (`src/`) on `sys.path`. So `python -m src.main` will NOT work; do not "fix" these into a package without updating every import.
- `pyproject.toml` script `stonkfish = "stonkfish:main"` points at `src/stonkfish/__init__.py`, which is a **non-functional stub** (`print("Hello from stonkfish!")`). Do not rely on it — it is not the app.
- The loop prompts for Elo (1320–2800) then color; typing moves as SAN (`e4`, `O-O`). `quit`/`exit` exits.

## The Stockfish binary is required and untracked

- `src/engine/stonk_engine.py` looks for the binary at `bin/stockfish` (relative to the module).
- `bin/` and `data/` are **gitignored**. `bin/stockfish` is a ~105MB Mach-O universal binary that is NOT in git — if it's missing, the engine crashes at runtime. Obtain/place it manually.

## Test / lint / typecheck / CI

- **pytest** is the test framework. `tests/` covers `core/game.py`, `ui/board_renderer.py`,
  and `engine/stonk_engine.py` (~19 tests). Run from repo root: `uv run pytest`.
- `pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["tests"]` under
  `[tool.pytest.ini_options]`, so flat imports (`from core.game import Game`) resolve
  without a conftest. `tests/test_stonk_engine.py` auto-skips when the Stockfish binary
  is absent (it checks `bin/stockfish` or `stockfish` on PATH).
- No ruff, mypy, or CI yet. The 5 `DeprecationWarning`s from `chess.engine` under
  Python 3.14 (asyncio event-loop policy) are harmless — they come from python-chess,
  not this repo.

## State

- Only Phase 1 (CLI) is built. Empty stubs waiting on later roadmap phases: `src/engine/base.py`, `src/engine/stockfish_uci.py`, `src/nnue/model.py`, `src/ui/cli.py`, `src/ui/tui.py`, `src/ui/gui.py`, `src/nnue/weights/`. See `roadmap.md` for the 5-phase plan. See `README.md` for the overview.
