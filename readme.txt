Tic-Tac-Toe Client/Server

A simple command-line Tic-Tac-Toe game that can be played between a client and a server using socket programming in Python.

Features

    Server and client modes for starting and joining games
    Ability for the client to choose X or O at the start of each game
    Server always makes the first move
    Communication of moves and game states between the client and server
    Support for replaying the game and graceful termination

Requirements

    Python 3.6 or higher

Usage

    Start the server on the desired port (defaults to 5131 if no port is specified):

           ex. python tictactoe.py -s [port]

    Connect a client to the server using the server's hostname and port:

         ex. python tictactoe.py -c [hostname] [port]
