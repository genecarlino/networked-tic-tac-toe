import sys
import socket
import argparse
from enum import Enum


# Default Port to be used if no port is specified
DEFAULT_PORT = 5131

# Enumeration for the two players
class Player(Enum):
    X = 'X'
    O = 'O'

# Class to represent the board
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

# Server function - sets up server, listens for client conn 
def server(port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen(1)
        print(f"Server started on port {port}, waiting for a client...")
        conn, addr = s.accept()
        with conn:
            print(f"Client connected from {addr}")
            play_game(conn, True)

# Client function that connects to a server
def client(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to server {host} on port {port}")
        play_game(s, False)

# Main function for playing the game
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

        # Setting the initial turn, server always goes first because client chose their player first
        my_turn = is_server

        # Game loop - continues until a player wins or the board is full (draw)
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
                # If it is the opponent's turn, wait for their move
                print("Waiting for the opponent's move...")
                move = sock.recv(1024).decode()
                row, col = map(int, move.split())
                board.make_move(row, col, opponent_player)
                # Display the updated board
                print(board)
                # Check if opponent has won
                if board.is_winner(opponent_player):
                    print("You lose!")
                    break
                # Switch turns
                my_turn = not my_turn

        print("Game over.")

        # Replay feature
        if is_server:
            # If the instance is the server, ask the player if they want to play again
            play_again_server = input("Do you want to play again? (y/n): ")

            # Send the server's decision to the client
            sock.sendall(play_again_server.encode())

            # Receive the client's decision about playing again
            play_again_client = sock.recv(1024).decode()
        else:
            # If the instance is the client, receive the server's decision about playing again
            play_again_server = sock.recv(1024).decode()

            # Ask the client player if they want to play again
            play_again_client = input("Do you want to play again? (y/n): ")

            # Send the client's decision to the server
            sock.sendall(play_again_client.encode())

        # If both players do not want to play again, close the connection and exit the loop
        if play_again_server.lower() != 'y' or play_again_client.lower() != 'y':
            print("Closing connection. Client and/or Server did not want to play again. Goodbye!")
            break

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe Client/Server")
    # Add mutually exclusive group for server and client
    group = parser.add_mutually_exclusive_group(required=True)
    # Add the server to the group
    group.add_argument("-s", "--server", action="store_true", help="Run as server")
    # Add the client to the group, expect a host as an additional argument
    group.add_argument("-c", "--client", metavar="HOST", help="Run as client and connect to server with the given host")
    # Add the default argument to the parser with a default port of 5131
    parser.add_argument("port", nargs="?", type=int, default=DEFAULT_PORT, help="Port to use (default: 5131)")

    args = parser.parse_args()

    # If server arg provided, run server function
    if args.server:
        server(args.port)
    # If client arg provided, run client function
    elif args.client:
        client(args.client, args.port)
    # If neither arg provided, print error message
    else:
        print("Invalid arguments. Please use -s or -c to specify server or client mode.")
    

#Sample Server Start : python3 ttt4.py -s\

#Sample Client Start : python3 ttt4.py -c localhost 5131