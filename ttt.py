import sys
import socket
import argparse
from typing import Tuple

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
    # List of possible winning patterns
    winning_patterns = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
        (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in winning_patterns:
        # Check if any of the winning patterns match
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]  # Return the winning player's character
    return ""  # Return an empty string if there is no winner


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

# Function to run the server instance of the networked Tic Tac Toe game
# Checks if the server or clients move is a winner

def server(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the server to the specified port
        s.bind(("", port))
        # Listen for incoming connections
        s.listen(1)
        print(f"Server ready. Listening on port {port}.")
        # Accept a connection
        conn, addr = s.accept()
        with conn: #ensure connection with be closed
            print(f"Connected by {addr}")
            # Initialize the board state
            board = " " * 9
            game_over = False
            while not game_over:
                # Print the current board state
                print_board(board)
                print("Your move enter an INT (0-8):")
                # Get the server player's move
                move = int(input())
                # Update the board and check for a winner
                board, game_over = handle_move(board, "X", move)
                if not game_over:
                    # Send the updated board state to the client
                    conn.sendall(board.encode())
                    # Receive the updated board state from the client
                    board = conn.recv(BUFFER_SIZE).decode()
                    # Check if the client's move resulted in a win
                    game_over = check_winner(board) != ""

# Function to run the client instance of the networked Tic Tac Toe game
def client(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        # Connect to the server at the specified host and port
        c.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        # Initialize the board state
        board = " " * 9
        game_over = False
        while not game_over:
            # Receive the updated board state from the server
            board = c.recv(BUFFER_SIZE).decode()
            # Check if the server's move resulted in a win
            game_over = check_winner(board) != ""
            if not game_over:
                # Print the current board state
                print_board(board)
                print("Your move, enter an INT (0-8):")
                # Get the client player's move
                move = int(input())
                # Update the board and check for a winner
                board, game_over = handle_move(board, "O", move)
                if not game_over:
                    # Send the updated board state to the server
                    c.sendall(board.encode())

# Main function to parse command-line arguments and launch the server or client instance
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Tic Tac Toe Game")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", action="store_true", help="Run in server mode")
    group.add_argument("-c", "--client", type=str, help="Run in client mode and connect to the specified host")
    parser.add_argument("port", nargs="?", default=DEFAULT_PORT, type=int, help="Port to listen on (server) or connect to (client), defaults to 5131")
    # Parse command-line arguments
    args = parser.parse_args()

    # Launch the server or client instance based on the parsed arguments
    if args.server:
        server(args.port)
    else:
        hostname = args.client
        client(hostname, args.port)

# Entry point for the script
if __name__ == "__main__":
    main()