This program allows two players to play a game of Tic Tac Toe across a network using the command line. The game can be run in server mode or client mode.
Requirements

    Python 3.6 or higher

Usage

    Save the provided Python code in a file named ttt.py.
    Use the command line to navigate to the directory containing the ttt.py file.
    Run the game in server mode or client mode.

Server Mode

To start the server, run:

css

python ttt.py -s [port]

Replace [port] with the port number on which you want the server to listen. If the port is omitted, it defaults to 5131.

Example:

yaml

python ttt.py -s 5131

Client Mode

To start the client, run:

css

python ttt.py -c [hostname] [port]

Replace [hostname] with the hostname or IP address of the device where the server is running. Replace [port] with the port number on which the server is listening. If the hostname or port is omitted, they default to the hostname of the device on which the client application is running and port 5131, respectively.

Example:

r

python ttt.py -c khoury.login.neu.edu 5131

Gameplay

The Tic Tac Toe board is represented as follows:

markdown

0 1 2
-----
3 4 5
-----
6 7 8

Each number (0-8) corresponds to a position on the board. Players take turns entering the number of the position where they want to place their mark (X for the server player and O for the client player).

The game continues until a player wins or the board is full, at which point the game will end and announce the result.