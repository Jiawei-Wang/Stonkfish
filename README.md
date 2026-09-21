# Stonkfish ♟️

A modular terminal chess application built in Python. It plays against the Stockfish engine (via UCI) in a plain-text CLI or an interactive Textual TUI, with a custom "StonkEngine" and NNUE evaluator planned for later phases.

## Architecture Roadmap

- **Phase 1: CLI & Core Logic** — ✅ Terminal interface with the `Stockfish` engine.
- **Phase 2: Terminal UI (TUI)** — ✅ Interactive Textual interface (board grid, eval meter, move history, mouse + SAN input). Keyboard navigation & drag-and-drop still to come.
- **Phase 3: StonkEngine (Backend)** — Custom move generation, Alpha-Beta Minimax search, and positional evaluation. (classical chess engine with no ML)
- **Phase 4: NNUE Evaluation** — PyTorch-trained Efficiently Updatable Neural Network for fast CPU evaluation.
- **Phase 5: Engine Switcher & GUI app** — Dynamic engine hot-swapping and graphical UI integration.

## Setup & Running

1. **Install dependencies**: `uv sync`
2. **Download the Stockfish binary and place it in the `bin/` folder**: https://stockfishchess.org/download/
3. **Run**: `uv run python src/main.py`

On launch you'll pick a mode — **1) CLI** (type moves as SAN) or **2) TUI** (Textual: click squares or type SAN) — then choose an Elo (1320–2800) and a color.
