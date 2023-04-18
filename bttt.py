import socket
import argparse

#TicTacToe class to handle basic game logic
class TicTacToe:
    def __init__(self, mark):
        self.board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        self.mark = mark

    def print_board(self):
        for i in range(3):
            for j in range(3):
                print(self.board[i][j], end='')
                if j != 2:
                    print('|', end='')
            if i != 2:
                print()
                print('-' * 5)
        print()

    def make_move(self, coordinates, mark):
        self.board[coordinates[0]][coordinates[1]] = mark
    
    def check_win(self, mark):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == mark:
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] == mark:
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == mark:
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] == mark:
            return True
        return False
    
    
    def check_game_end(self, mark):
    # check for win and return True if so
        if self.check_win(mark):
            if mark == self.mark:
                print('You won')
            else:
                print('You lost')
            return True

        # check for tie and return True if so
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == ' ':
                    return False
        print('Tie')
        return True
    
    #check to see that move is in board space and space is empty
    def check_valid_move(self, coordinates):
        if coordinates[0] < 0 or coordinates[0] > 2 or coordinates[1] < 0 or coordinates[1] > 2:
            return False
        if self.board[coordinates[0]][coordinates[1]] == ' ':
            return True
        return False

#create client and connect to server, prompt for mark
def init_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #close socket after a min
    client.settimeout(60)
    client.connect((args.ip, args.port))
    client_mark = input("Enter your mark (X/O): ")
    if client_mark == 'X':
        server_mark = 'O'
    else:
        server_mark = 'X'
    
    return client, client_mark, server_mark

#determine if move is vaild, prompt user unitl valid move is entered, handle quit
def handle_client_move(game):
    # ensure valie move
    valid_move = False
    while not valid_move:
        user_input = input("Enter your move as row and column indicies (e.g. top left: 0 0, bottom right: 2 2) or q for quit: ")
        if user_input == 'q':
            return 'q'
        client_move = user_input.split()
        if len(client_move) != 2 or not (valid_move := game.check_valid_move([int(client_move[0]), int(client_move[1])])):
            print("Invalid move, try again")
    return client_move

#main client loop
def run_client():
    #creat client and connect to server
    client, client_mark, server_mark = init_client()
    #start game with client mark
    game = TicTacToe(client_mark)
    #send client mark to server
    client.sendall(client_mark.encode())
    try:
        while True:
            # check if still connected to server
            if not (server_msg := client.recv(1024)):
                print("Server disconnected")
                break

            #parse server msg for move and make move
            server_move = server_msg.decode().split()
            game.make_move([int(server_move[0]), int(server_move[1])], server_mark)
            game.print_board()

            if game.check_game_end(server_mark):
                break

            client_move = handle_client_move(game)
            if client_move == 'q':
                break
            
            #make move and send to server
            game.make_move([int(client_move[0]), int(client_move[1])], client_mark)
            client.sendall(f'{client_move[0]} {client_move[1]}'.encode())
            game.print_board()

            if game.check_game_end(client_mark):
                break

    except socket.timeout:
        print("Server disconnected")

    client.close()

#accept connections and receive client mark, set server mark appropriately
def server_accept_connections(server):
    # accept connections
    conn, addr = server.accept()
    print('Connected by', addr)
    #close socket after a min
    conn.settimeout(60)
    # receive client mark
    client_mark = conn.recv(1024).decode()
    if client_mark == 'X':
        server_mark = 'O'
    else:
        server_mark = 'X'

    return conn, client_mark, server_mark

#determine if move is vaild, prompt user unitl valid move is entered
def handle_server_move(game):
    valid_move = False
    while not valid_move:
        user_input = input("Enter your move as row and column indicies (e.g. top left: 0 0, bottom right: 2 2): ")
        server_move = user_input.split()
        if len(server_move) != 2 or not (valid_move := game.check_valid_move([int(server_move[0]), int(server_move[1])])):
            print("Invalid move, try again")
    
    return server_move


#main server loop
def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # bind to port and listen
        server.bind(('', args.port))
        server.listen()
        while True:
            # accept connections
            conn, client_mark, server_mark = server_accept_connections(server)
            # start game
            game = TicTacToe(server_mark)
            try:
                while True:
                    # ensure valid move or quit
                    server_move = handle_server_move(game)
                    game.make_move([int(server_move[0]), int(server_move[1])], server_mark)

                    # send server move to client
                    conn.sendall(f'{server_move[0]} {server_move[1]}'.encode())
                    game.print_board()

                    # check for win and break out of loop if so
                    if game.check_game_end(server_mark):
                        print("Waiting for client...")
                        break

                    # get client move, check for quit and break if so
                    if not (client_msg := conn.recv(1024)):
                        print('Client disconnected, waiting for new connections...')
                        break

                    client_move = client_msg.decode().split()
                    game.make_move([int(client_move[0]), int(client_move[1])], client_mark)
                    game.print_board()

                    # check for win and break out of loop if so
                    if game.check_game_end(client_mark):
                        print("Waiting for client...")
                        break
    
            except socket.timeout:
                print("Client disconnected, waiting for new connections...")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Networked Tic-Tac-Toe')
    parser.add_argument('-c', '--client', action='store_true', help='Run as client')
    parser.add_argument('-s', '--server', action='store_true', help='Run as server')
    parser.add_argument('-p', '--port', type=int, default=5131, help='Port to use')
    parser.add_argument('-i', '--ip', type=str, default='khoury.login.neu.edu', help='IP address to connect to')
    args = parser.parse_args()

    # run as client
    if args.client:
        print('Running in Client Mode')
        while True:
            run_client()
            reset_game = input('Press enter to play again or type "q" to quit: ')
            if reset_game == 'q':
                break

    # run as server
    if args.server:
        print('Running in Server Mode')
        run_server()