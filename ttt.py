import sys
import socket
import argparse
from typing import Tuple

DEFAULT_PORT = 5131
BUFFER_SIZE = 1024

def print_board(board: str) -> None:
    for i in range(0, 9, 3):
        print(" ".join(board[i:i + 3]))
        if i < 6:
            print("-----")

def check_winner(board: str) -> str:
    winning_patterns = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
        (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)
    ]
    for a, b, c in winning_patterns:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return ""

def handle_move(board: str, player: str, move: int) -> Tuple[str, bool]:
    if 0 <= move < 9 and board[move] == " ":
        board = board[:move] + player + board[move + 1:]
        winner = check_winner(board)
        if winner:
            print_board(board)
            print(f"Player {player} wins!")
            return board, True
        return board, False
    else:
        print("Invalid move. Try again.")
        return board, False

def server(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", port))
        s.listen(1)
        print(f"Server ready. Listening on port {port}.")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            board = " " * 9
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

def client(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        board = " " * 9
        game_over = False
        while not game_over:
            board = s.recv(BUFFER_SIZE).decode()
            game_over = check_winner(board) != ""
            if not game_over:
                print_board(board)
                print("Your move (0-8):")
                move = int(input())
                board, game_over = handle_move(board, "O", move)
                if not game_over:
                    s.sendall(board.encode())

def main():
    parser = argparse.ArgumentParser(description="Tic Tac Toe Game")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", action="store_true", help="Run in server mode")
    group.add_argument("-c", "--client", type=str, help="Run in client mode and connect to the specified host")
    parser.add_argument("port", nargs="?", default=DEFAULT_PORT, type=int, help="Port to listen on (server) or connect to (client), defaults to 5131")
    args = parser.parse_args()

    if args.server:
        server(args.port)
    else:
        hostname = args.client
        client(hostname, args.port)

if __name__ == "__main__":
    main()

