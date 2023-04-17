import sys
import socket
import argparse
from enum import Enum
from typing import Tuple

#Default Port to be used if no port is specified
DEFAULT_PORT = 5131

#Enumeration for the two players
class Player(Enum):
    X = 'X'
    O = 'O'

#Class to represent the board
class Board:
    def __init__(self):
        #Initialize the board to be empty, 3x3
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
    # Method to make a move on the board
    def make_move(self, row: int, col: int, player: Player) -> bool:
        if self.board[row][col] == ' ':
            self.board[row][col] = player.value
            return True
        return False
    # Method to check if a player has won
    def is_winner(self, player: Player) -> bool:
        for i in range(3):
            if all(self.board[i][j] == player.value for j in range(3)) or all(self.board[j][i] == player.value for j in range(3)):
                return True

        if all(self.board[i][i] == player.value for i in range(3)) or all(self.board[i][2 - i] == player.value for i in range(3)):
            return True

        return False
    # Method to check if the board is full
    def is_full(self) -> bool:
        return all(self.board[i][j] != ' ' for i in range(3) for j in range(3))
    # Method to return a string representation of the board
    def __str__(self) -> str:
        return '\n'.join([' '.join(self.board[i]) for i in range(3)])

#Server function - sets up server, listens for client conn 
def server(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen(1)
        print(f"Server started on port {port}, waiting for a client...")
        conn, addr = s.accept()
        with conn:
            print(f"Client connected from {addr}")
            play_game(conn, True)

#client function that connects to a server
def client(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to server {host} on port {port}")
        play_game(s, False)

#main function for playing the game
def play_game(sock: socket.socket, is_server: bool):
    while True:
        #innit new game board
        board = Board()

        #determine players
        if is_server:
            opponent_choice = sock.recv(1024).decode()
            opponent_player = Player[opponent_choice]
            my_player = Player.O if opponent_player == Player.X else Player.X
        else:
            #if instance is client, ask the user for their choice, and send it to the server
            choice = input("Choose your player (X/O): ").upper()
            while choice not in ["X", "O"]:
                choice = input("Invalid choice. Choose your player (X/O): ").upper()

            my_player = Player[choice]
            opponent_player = Player.O if my_player == Player.X else Player.X
            sock.sendall(choice.encode())

        #setting the initial turn, server always goes first because client chose their player first
        my_turn = is_server

        #Game loop - continues until a player wins or the board is full (draw)
        while True:
            if my_turn:
                #if it is the player's turn, ask for their move, and send it to the server
                print("Your turn:")
                move = input("Enter your move (row col): ")
                row, col = map(int, move.split())
                #if move is valid, send the move to the opponent or print invalid move 
                if board.make_move(row, col, my_player):
                    sock.sendall(move.encode())
                    print(board)
                    #check if current player has won, or if the board is full (draw)
                    if board.is_winner(my_player):
                        print("You win!")
                        break
                    elif board.is_full():
                        print("It's a draw!")
                        break
                    #switch turns
                    my_turn = not my_turn
                else:
                    print("Invalid move. Try again.")
            else:
                #if it is the opponent's turn, wait for their move
                print("Waiting for the opponent's move...")
                move = sock.recv(1024).decode()
                row, col = map(int, move.split())
                board.make_move(row, col, opponent_player)
                #display the updated board
                print(board)
                #check if opponent has won
                if board.is_winner(opponent_player):
                    print("You lose!")
                    break
                #switch turns
                my_turn = not my_turn

        print("Game over.")

        # Replay feature
        #ask the user if they want to play again, and send their response to the client
        if is_server:
            play_again = input("Do you want to play again? (y/n): ")
            sock.sendall(play_again.encode())
        else:
            #if instance is client, wait for the server's response and recive that response
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

