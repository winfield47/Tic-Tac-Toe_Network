# TicTacToe Server
# Kyle Winfield Burnham

# Black Hat Python by Justin Seitz and Tim Arnold
# https://learning.oreilly.com/library/view/black-hat-python/9781098128906/c02.xhtml#h1-501126c02-0004

import socket
import threading
import random

# What IP I am listening to:
IP = '0.0.0.0'
# What Port I am listening on:
PORT = 10101


def isGameOver(gameData):
    gameBoard = gameData[4:]
    win_conditions = [
        # Rows
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        # Columns
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        # Diagonals
        [0, 4, 8], [2, 4, 6]
    ]

    if 0 not in gameBoard:
        gameData[3] = 3
        return True  # It's a draw, all spaces are filled
    for condition in win_conditions:
        a, b, c = condition
        if gameBoard[a] == gameBoard[b] == gameBoard[c] == 1:
            gameData[3] = 4
            return True  # Player has won
        if gameBoard[a] == gameBoard[b] == gameBoard[c] == 2:
            gameData[3] = 5
            return True  # Computer has won

    return False  # The game is not over yet


def convertSpotValue(spot):
    if spot == 0:
        return " "
    if spot == 1:
        return "O"
    if spot == 2:
        return "X"
    else:
        return "ERROR"


def printGameBoard(spots):
    print("+---+---+---+")
    count = 0
    for spot in spots:
        print("| " + convertSpotValue(spot), end=" ")
        count += 1
        if count % 3 == 0:
            print("|\n+---+---+---+")


def computerTurn(gameData):
    empty_spots = [i for i in range(9) if gameData[i + 4] == 0]
    if empty_spots:
        computer_choice = random.choice(empty_spots)
        gameData[4 + computer_choice] = 2  # Computer's move (2 for X)
        gameData[3] = 2
    else:
        print("It's a draw!")


def displayDiagnostics(gameData):
    # print the game data
    if gameData[3] == 1:
        print("O's turn:")
    elif gameData[3] == 2:
        print("X's turn:")
    elif gameData[3] == 3:
        print("Cat's game...")
    elif gameData[3] == 4:
        print("O wins!")
    elif gameData[3] == 5:
        print("X wins!")
    elif gameData[3] == 0:
        print(f"[*] Game start!")
    else:
        print("ERROR")
    print(f"[*] Send count: {gameData[2]}")
    printGameBoard(gameData[4:])


# to take a type 2 protocol and update the game state
def updateGameData(client_data):
    print("DEBUG")


# Listen for connections
def main():
    # make a TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((IP, PORT))
        # we don't need a large backlog (5)
        server.listen(5)
        print(f'[*] Listening on {IP}:{PORT}')

        # Continuously listen for clients from any address (0.0.0.0)
        while True:
            # Get the client
            client, address = server.accept()
            # print(f'[*] Accepted connection from {address[0]}:{address[1]}')

            # Here is the function call:
            client_handler = threading.Thread(target=handle_client, args=(client, address[0], address[1]))
            client_handler.start()
    except OSError as os:
        print("OSError: Address already in use.")
    except KeyboardInterrupt as ki:
        print("\n[*] Exiting...")
    

# Send data back to the connecting client:
def handle_client(client_socket, address, port):
    with client_socket as sock:
        try:
            print(f'[*] Accepted connection from {address}:{port}')
            gameData = [0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            displayDiagnostics(gameData)

            while True:

                # get the game data from client
                received_data = sock.recv(1024)
                gameData[2] += 1
                response_raw = received_data.decode()
                client_request = list(map(int, response_raw.split(',')))

                # client move request type
                if client_request[0] == 2:

                    # check to see if the requested spot is available
                    requested_spot = 3 + client_request[2]
                    if gameData[requested_spot] == 0:

                        # commit client's turn
                        gameData[3] = 1
                        gameData[requested_spot] = 1
                        displayDiagnostics(gameData)

                        # take a turn
                        if not isGameOver(gameData):
                            # X's turn attempted
                            gameData[3] = 2
                            computerTurn(gameData)
                        displayDiagnostics(gameData)

                        # game over?
                        if isGameOver(gameData):

                            # convert data to a format that can be sent through a socket
                            gameDataStr = ','.join(map(str, gameData))

                            # send the data
                            sock.send(gameDataStr.encode())
                            gameData[2] += 1

                            # reset the game information but keep send-count
                            print(f"[*] Game data before reset: {gameData}")
                            gameData[4:] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                            print(f"[*] Game data after reset:  {gameData}")

                        else:

                            # convert data to a format that can be sent through a socket
                            gameDataStr = ','.join(map(str, gameData))

                            # send the data
                            sock.send(gameDataStr.encode())
                            gameData[2] += 1

                    else:

                        # convert data to a format that can be sent through a socket
                        gameData[3] = 1
                        gameDataStr = ','.join(map(str, gameData))

                        # send the data
                        sock.send(gameDataStr.encode())
                        gameData[2] += 1

                        print("[*] Client requested an occupied space.")

                # type terminate game type
                elif client_request[0] == 1:
                    print(f"[*] Disconnected from {address}:{port}")
                    break

        except ValueError as ve:
            print("[*] ValueError: ", format(ve.args[0]))
            print("[*] Disconnected.")
        except KeyboardInterrupt as ki:
            print("\n[*] Exiting...")


# START
if __name__ == '__main__':
    main()  
    

