# Stonkfish Development Roadmap

---

### Phase 1: Basic App & Terminal Interface (CLI)
* **Board & Game Rules:** Use `python-chess` to manage chess rules, piece movements, and game states (check, checkmate, draws).
* **Stockfish Wrapper:** Link the standard Stockfish binary executable to Python using `python-chess.engine` to fetch top engine moves via UCI behind the scenes[cite: 1, 3].
* **Algebraic Notation:** Allow users to input moves using standard chess notation (e.g., `e4`, `Nf3`, `O-O`) instead of raw square coordinates (like `e2e4`).
* **Basic Text Display:** Output the board state to the terminal as simple ASCII/Unicode characters after every move.

---

### Phase 2: Terminal UI (TUI) & Controls
* **Interactive TUI Layout:** Use a Python library like `Textual` or `Blessed` to create a terminal UI with a visual board grid, move history panel, and current game evaluation meter.
* **Keyboard Navigation:** Add arrow key or `WASD` navigation to move a selector highlight across the board squares, using `Space`/`Enter` to pick up and drop pieces.
* **Mouse Support:** Add clickable board squares and drag-and-drop support using terminal mouse event tracking.

---

### Phase 3: Custom Chess Engine ("StonkEngine")
* **Move Generation & Board State:** Build your own custom backend board representation (e.g., bitboards or board arrays)[cite: 3, 4].
* **Minimax & Search Optimization:** Implement a **Negamax** search algorithm featuring **Alpha-Beta Pruning**, transposition tables, and move ordering to efficiently evaluate search trees[cite: 3].
* **Handcrafted Evaluation:** Implement basic positional evaluation scoring based on standard piece values and piece-square tables[cite: 3].

---

### Phase 4: Custom Neural Network (NNUE)
* **NNUE Model Architecture:** Build a small Neural Network Efficiently Updatable (NNUE) model using `PyTorch` optimized for quick CPU evaluations[cite: 2, 3].
* **Data & Training:** Generate a dataset of chess positions using engine self-play or game logs, then train the neural network to output board evaluations[cite: 3].
* **Engine Integration:** Plug your trained NNUE weights into your custom engine’s evaluation function[cite: 1, 3].

---

### Phase 5: Engine Selection & Graphical UI (GUI)
* **Engine Switcher:** Add a menu in the TUI that lets players choose whether to play against Stockfish or your custom engine before or during a game.
* **Future GUI:** Port the front-end to a graphical library like `Pygame`, `PyQt`, or `CustomTkinter` while keeping the underlying backend engine interfaces intact.