"""Command-line entry point for the Stonkfish chess app.

Wires together the Stockfish engine, the game state, and the board
renderer to run an interactive CLI match. The player picks an Elo rating
and a color, then plays against the engine by entering moves in Standard
Algebraic Notation (SAN).
"""

import sys
import os
import chess
from core.game import Game
from engine.stonk_engine import StonkEngine
from cli_ui.board_renderer import render_board
from tui_ui.app import StonkfishTUI


def select_mode() -> str:
    """Prompt the user to select a mode (CLI or TUI).
    
    Returns:
        str: '1' for CLI and '2' for TUI
    """
    print("\n=== Welcome to Stonkfish Chess ===")
    print("1) Play in CLI Mode")
    print("2) Play in TUI Mode (Textual)")
    print("3) Exit")

    while True:
        try:
            choice = input("\nSelect mode (1/2/3) [Default 2]: ").strip()
            if not choice or choice == "2":
                return "2"
            if choice == "1":
                return "1"
            if choice == "3" or choice.lower() in ["q", "quit", "exit"]:
                print("Goodbye!")
                os._exit(0)  # Force immediate process termination
            print("Invalid option. Please enter 1, 2, or 3.")
        except EOFError:
            # Re-open standard input if Textual altered stdin state
            sys.stdin = open(0, "r", os.O_RDONLY)
            print()


def setup_cli_game():
    """Collect the player's match preferences from the terminal.

    Prompts for a Stockfish Elo rating (clamped to the supported range)
    and the color the player wants to play.

    Returns:
        tuple[int, chess.Color]: The chosen Elo rating and the player's
        side to play.
    """
    print("=== Welcome to Stonkfish CLI ===")

    # Prompt until the player supplies a valid Elo within the supported range.
    while True:
        try:
            elo_input = input("Select Stockfish Elo (1320 - 2800) [Default 1500]: ").strip()
            elo = int(elo_input) if elo_input else 1500
            if 1320 <= elo <= 2800:
                break
            print("Please enter a value between 1320 and 2800.")
        except ValueError:
            print("Invalid number format.")

    # Map the color choice to a chess.Color; anything but 'b' defaults to White.
    side_choice = input("Play as White or Black? (w/b) [Default w]: ").strip().lower()
    player_color = chess.BLACK if side_choice == 'b' else chess.WHITE

    return elo, player_color


def run_cli_mode():
    """Run the interactive CLI game loop.

    Initializes the engine, gathers the player's settings, and alternates
    between the player's moves and the engine's responses until the game
    ends or the player quits. Always shuts the engine down on exit.
    """
    try:
        engine = StonkEngine()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    game = None
    player_color = None
    # Tracks whether setup completed, so the final board is only shown for a real game.
    entered_game = False
    try:
        elo, player_color = setup_cli_game()
        engine.configure_elo(elo)
        game = Game()
        entered_game = True

        print("\nGame starting! Enter moves using Standard Algebraic Notation (e.g., e4, Nf3, O-O).\n")

        while not game.is_over():
            # Render the board from the player's perspective.
            print(render_board(game.board, invert=(player_color == chess.BLACK)))

            if game.board.turn == player_color:
                san_input = input("\nYour move: ").strip()
                if san_input.lower() in ['quit', 'exit']:
                    print("Exiting game...")
                    break

                if not game.make_player_move(san_input):
                    print("Illegal move or invalid SAN notation. Try again!")
                    continue
            else:
                print("\nStonkfish is thinking...")
                engine_move = engine.get_best_move_and_eval(game.board, time_limit=0.5)
                played_san = game.make_engine_move(engine_move[0])
                print(f"Stonkfish played: {played_san}")

    except KeyboardInterrupt:
        print("\nInterrupted. Quitting...")
    finally:
        engine.quit()

    if game and entered_game:
        print("\n" + render_board(game.board, invert=(player_color == chess.BLACK)))
        if game.is_over():
            print(f"\nGame Over! Result: {game.get_result()}")


def run_tui_mode():
    """Run the interactive TUI game loop."""
    app = StonkfishTUI()
    app.run()


def main():
    while True:
        try:
            mode = select_mode()
            if mode == "1":
                run_cli_mode()
            elif mode == "2":
                run_tui_mode()
        except KeyboardInterrupt:
            print("\nInterrupted. Quitting...")
            os._exit(0)


if __name__ == "__main__":
    main()
