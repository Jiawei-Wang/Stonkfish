# Stonkfish

Modular Python chess app with a CLI and a Textual TUI. Uses `python-chess` for
rules and a Stockfish binary (`bin/stockfish`) over UCI for move generation.

## Environment

- Package manager: **`uv`** (not pip/a raw venv). Python 3.14 is pinned in `.python-version`.
- Install deps: `uv sync`. Runtime deps are `chess` (imported as `chess`; pip name `python-chess`) and `textual` (the TUI framework).
- `requirements.txt` is **stale/misleading** (`python-chess>=1.999`). Trust `pyproject.toml` + `uv.lock`.

## Running

- Real entrypoint is **`src/main.py`**. Run from repo root: `uv run python src/main.py`.
- Imports in `src/` are **flat** (`from core.game import Game`, `from cli_ui.board_renderer import render_board`, not `from src.core...`). They resolve because Python puts the script's directory (`src/`) on `sys.path`. So `python -m src.main` will NOT work; do not "fix" these into a package without updating every import.
- `pyproject.toml` script `stonkfish = "stonkfish:main"` points at `src/stonkfish/__init__.py`, which is a **non-functional stub** (`print("Hello from stonkfish!")`). Do not rely on it — it is not the app.
- On launch a mode menu is shown: **1) CLI**, **2) TUI** (default), **3) Exit**.
  - **CLI mode** prompts for Elo (1320–2800) then color, then a plain-text loop where you type moves as SAN (`e4`, `O-O`); `quit`/`exit` ends the game.
  - **TUI mode** opens a Textual app: a setup modal (Elo + color), then a board grid, eval meter, move history, and a SAN input bar. Click squares to move or type SAN; `q` quits.

## The Stockfish binary is required and untracked

- `src/engine/stonk_engine.py` looks for the binary at `bin/stockfish` (relative to the module).
- `bin/` and `data/` are **gitignored**. `bin/stockfish` is a ~105MB Mach-O universal binary that is NOT in git — if it's missing, the engine crashes at runtime. Obtain/place it manually.

## Test / lint / typecheck / CI

- **pytest** is the test framework. `tests/` covers `core/game.py`, `cli_ui/board_renderer.py`, and `engine/stonk_engine.py` (20 tests). Run from repo root: `uv run pytest`.
- `pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["tests"]` under `[tool.pytest.ini_options]`, so flat imports (`from core.game import Game`) resolve without a conftest. `tests/test_stonk_engine.py` auto-skips its 4 binary-dependent tests when the Stockfish binary is absent (it checks `bin/stockfish` or `stockfish` on PATH).
- **Known failure:** 2 engine tests (`test_get_best_move_*`) still call the old `get_best_move()` name, which was renamed to `get_best_move_and_eval()` — they fail when the binary is present.
- No ruff, mypy, or CI yet. The 5 `DeprecationWarning`s from `chess.engine` under Python 3.14 (asyncio event-loop policy) are harmless — they come from python-chess, not this repo.

## State

- **Phase 1 (CLI) and Phase 2 (TUI MVP) are built.** See `roadmap.md` for the 5-phase plan and `README.md` for the overview.
- Layout: `src/core/game.py` (board/move state), `src/engine/stonk_engine.py` (Stockfish UCI wrapper), `src/cli_ui/board_renderer.py` (text board), `src/tui_ui/` (Textual app + `widgets/` board, eval meter, input, move history), `src/main.py` (entrypoint + mode menu).
- Remaining stubs for later phases: `src/nnue/model.py` (empty) and `src/nnue/weights/` (empty dir). The custom engine (Phase 3) and NNUE (Phase 4) are not started; there is no GUI yet (Phase 5).
