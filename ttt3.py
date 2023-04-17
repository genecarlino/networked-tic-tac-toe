import sys
import socket
import argparse
from typing import Tuple
import os

# Constants
DEFAULT_PORT = 5131
BUFFER_SIZE = 1024

# Function to print the Tic Tac Toe board to the console
def print_board(board: str) -> None:
    for i in range(0, 9, 3):
        # Print each row of the board
        print(" ".join(board[i:i + 3]))
        if i < 6:
            # Print horizontal dividers between rows
            print("-----")

# Function to check if there is a winner in the current board state
def check_winner(board: str) -> str:
    win_positions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                     (0, 3, 6), (1, 4, 7), (2, 5, 8),
                     (0, 4, 8), (2, 4, 6)]
    for a, b, c in win_positions:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return ""

# Function to handle a player's move, update the board, and check for a winner
def handle_move(board: str, player: str, move: int) -> Tuple[str, bool]:
    # Check if the move is valid - space is empty and within the board
    if 0 <= move < 9 and board[move] == " ":
        # Update the board with the player's move
        board = board[:move] + player + board[move + 1:]
        # Check if the move resulted in a win
        winner = check_winner(board)
        if winner:
            # Print the updated board and a winning message
            print_board(board)
            print(f"Player {player} wins!")
            return board, True  # Return the updated board and a flag indicating the game is over
        return board, False  # Return the updated board and a flag indicating the game is not over
    else:
        # Print an error message for an invalid move
        print("Invalid move. Try again.")
        return board, False  # Return the unchanged board and a flag indicating the game is not over

def server(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", port))
        s.listen(1)
        print(f"Server ready. Listening on port {port}.")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            replay = "yes"
            while replay.lower() == "yes":
                board = " " * 9  # Reset the board at the beginning of each game
                game_over = False
                while not game_over:
                    print_board(board)
                    print("Your move (0-8):")
                    move = int(input())
                    board, game_over = handle_move(board, "X", move)
                    if not game_over:
                        conn.sendall(board.encode())
                        board = conn.recv(BUFFER_SIZE).decode()
                        game_over = check_winner(board) != ""
                print("Game over")
                replay = conn.recv(BUFFER_SIZE).decode()  # Wait for the replay decision from the client
                conn.sendall(replay.encode())  # Send the replay decision back to the client
                if replay.lower() == "yes":
                    board = " " * 9
                    conn.sendall(board.encode())  # Send the reset board to the client



def client(address: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((address, port))
        print("Connected to the server.")

        replay = "yes"
        while replay.lower() == "yes":
            game_over = False
            while not game_over:
                board = sock.recv(BUFFER_SIZE).decode()

                if board == "yes":
                    continue

                print_board(board)
                game_over = check_winner(board) != ""

                if not game_over:
                    print("Your turn")
                    move = input("Your move (0-8): ")
                    board, game_over = handle_move(board, "O", int(move))
                    if not game_over:
                        sock.sendall(board.encode())
                    else:
                        print("Game over")
                else:
                    print("Waiting for opponent's move...")
                    print("Game over")

            replay = input("Do you want to play again? (yes/no): ").lower()
            sock.sendall(replay.encode())

            if replay == "yes":
                server_replay_decision = sock.recv(BUFFER_SIZE).decode()
                if server_replay_decision.lower() == "yes":
                    board = " " * 9
                    sock.sendall(board.encode())  # Send the reset board to the server
                else:
                    print("Server decided not to play again.")
                    break
            else:
                break






def main():
    parser = argparse.ArgumentParser(description="Networked Tic Tac Toe")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", nargs='?', const=DEFAULT_PORT, metavar="PORT", type=int, help="Run as server, listening on PORT (defaults to 5131)")
    group.add_argument("-c", "--client", action="store_true", help="Run as client, connecting to server")
    parser.add_argument("--host", default="localhost", metavar="HOST", help="Specify the host to connect as a client (defaults to localhost)")
    parser.add_argument("-p", "--port", default=DEFAULT_PORT, metavar="PORT", type=int, help="Specify the port to connect or listen (defaults to 5131)")

    args = parser.parse_args()

    if args.server:
        server(args.port)
    else:
        client(args.host, args.port)

if __name__ == "__main__":
    main()