"""Command-line entry point for the Stonkfish chess app.

Wires together the Stockfish engine, the game state, and the board
renderer to run an interactive CLI match. The player picks an Elo rating
and a color, then plays against the engine by entering moves in Standard
Algebraic Notation (SAN).
"""

import chess
from core.game import Game
from engine.stonk_engine import StonkEngine
from ui.board_renderer import render_board


def setup_game():
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


def main():
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
        elo, player_color = setup_game()
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
                engine_move = engine.get_best_move(game.board, time_limit=0.5)
                played_san = game.make_engine_move(engine_move)
                print(f"Stonkfish played: {played_san}")

    except KeyboardInterrupt:
        print("\nInterrupted. Quitting...")
    finally:
        engine.quit()

    if game and entered_game:
        print("\n" + render_board(game.board, invert=(player_color == chess.BLACK)))
        if game.is_over():
            print(f"\nGame Over! Result: {game.get_result()}")


if __name__ == "__main__":
    main()
