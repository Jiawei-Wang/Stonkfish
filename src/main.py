import chess
from core.game import Game
from engine.stonk_engine import StonkEngine
from ui.board_renderer import render_board

def setup_game():
    print("=== Welcome to Stonkfish CLI ===")
    
    # Configure Elo
    while True:
        try:
            elo_input = input("Select Stockfish Elo (1320 - 2800) [Default 1500]: ").strip()
            elo = int(elo_input) if elo_input else 1500
            if 1320 <= elo <= 2800:
                break
            print("Please enter a value between 1320 and 2800.")
        except ValueError:
            print("Invalid number format.")

    # Configure Side
    side_choice = input("Play as White or Black? (w/b) [Default w]: ").strip().lower()
    player_color = chess.BLACK if side_choice == 'b' else chess.WHITE

    return elo, player_color


def main():
    try:
        engine = StonkEngine()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    game = None
    player_color = None
    entered_game = False
    try:
        elo, player_color = setup_game()
        engine.configure_elo(elo)
        game = Game()
        entered_game = True

        print("\nGame starting! Enter moves using Standard Algebraic Notation (e.g., e4, Nf3, O-O).\n")

        while not game.is_over():
            # Display board from player perspective
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