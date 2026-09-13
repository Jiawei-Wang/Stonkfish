# Stonkfish ♟️

A modular terminal and graphical chess application built in Python. Features UCI support for external engines (Stockfish) alongside a built-in custom chess engine with an NNUE neural network evaluator ("StonkEngine").

## Architecture Roadmap

- **Phase 1: CLI & Core Logic** — Terminal interface with `python-chess` rules enforcement.
- **Phase 2: Terminal UI (TUI)** — Rich interactive interface built with keyboard & mouse support.
- **Phase 3: StonkEngine (Backend)** — Custom move generation, Alpha-Beta Minimax search, and positional evaluation. (classical chess engine with no ml)
- **Phase 4: NNUE Evaluation** — PyTorch-trained Efficiently Updatable Neural Network for fast CPU evaluation.
- **Phase 5: Engine Switcher & GUI** — Dynamic engine hot-swapping and graphical UI integration.

## Setup & Running
