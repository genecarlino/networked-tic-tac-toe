import sys
import socket
import argparse
from enum import Enum
from typing import Tuple

DEFAULT_PORT = 5131

class Player(Enum):
    X = 'X'
    O = 'O'

class Board:
    def __init__(self):
        self.board = [[' ' for _ in range(3)] for _ in range(3)]

    def make_move(self, row: int, col: int, player: Player) -> bool:
        if self.board[row][col] == ' ':
            self.board[row][col] = player.value
            return True
        return False

    def is_winner(self, player: Player) -> bool:
        for i in range(3):
            if all(self.board[i][j] == player.value for j in range(3)) or all(self.board[j][i] == player.value for j in range(3)):
                return True

        if all(self.board[i][i] == player.value for i in range(3)) or all(self.board[i][2 - i] == player.value for i in range(3)):
            return True

        return False

    def is_full(self) -> bool:
        return all(self.board[i][j] != ' ' for i in range(3) for j in range(3))

    def __str__(self) -> str:
        return '\n'.join([' '.join(self.board[i]) for i in range(3)])

def server(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen(1)
        print(f"Server started on port {port}, waiting for a client...")
        conn, addr = s.accept()
        with conn:
            print(f"Client connected from {addr}")
            play_game(conn, True)

def client(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to server {host} on port {port}")
        play_game(s, False)

def play_game(sock: socket.socket, is_server: bool):
    while True:
        board = Board()

        if is_server:
            opponent_choice = sock.recv(1024).decode()
            opponent_player = Player[opponent_choice]
            my_player = Player.O if opponent_player == Player.X else Player.X
        else:
            choice = input("Choose your player (X/O): ").upper()
            while choice not in ["X", "O"]:
                choice = input("Invalid choice. Choose your player (X/O): ").upper()

            my_player = Player[choice]
            opponent_player = Player.O if my_player == Player.X else Player.X
            sock.sendall(choice.encode())

        my_turn = is_server

        while True:
            if my_turn:
                print("Your turn:")
                move = input("Enter your move (row col): ")
                row, col = map(int, move.split())
                if board.make_move(row, col, my_player):
                    sock.sendall(move.encode())
                    print(board)
                    if board.is_winner(my_player):
                        print("You win!")
                        break
                    elif board.is_full():
                        print("It's a draw!")
                        break
                    my_turn = not my_turn
                else:
                    print("Invalid move. Try again.")
            else:
                print("Waiting for the opponent's move...")
                move = sock.recv(1024).decode()
                row, col = map(int, move.split())
                board.make_move(row, col, opponent_player)
                print(board)
                if board.is_winner(opponent_player):
                    print("You lose!")
                    break
                my_turn = not my_turn

        print("Game over.")

        # Replay feature
        if is_server:
            play_again = input("Do you want to play again? (y/n): ")
            sock.sendall(play_again.encode())
        else:
            play_again = sock.recv(1024).decode()

        if play_again.lower() != 'y':
            print("Closing connection.")
            break





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe Client/Server")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-s", "--server", action="store_true", help="Run as server")
    group.add_argument("-c", "--client", metavar="HOST", help="Run as client and connect to server with the given host")
    parser.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT, help="Port to use (default: 5131)")

    args = parser.parse_args()

    if args.server:
        server(args.port)
    elif args.client:
        client(args.client, args.port)
    else:
        print("Invalid arguments. Please use -s or -c to specify server or client mode.")

