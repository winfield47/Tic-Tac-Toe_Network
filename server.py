# TicTacToe Server
# Kyle Winfield Burnham

# Black Hat Python by Justin Seitz and Tim Arnold
# https://learning.oreilly.com/library/view/black-hat-python/9781098128906/c02.xhtml#h1-501126c02-0004

import socket
import threading
import random
import time

# What IP I am listening to:
IP = '0.0.0.0'
# What current_port I am listening on:
current_port = 10101


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
        return "convertSpotValue ERROR"


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


def displayDiagnostics(gameData, current_port):
    # print the game data
    print(f"[*] Players: {players}")
    if gameData[3] == 1:
        print(f"[*] O's turn: {current_port}")
    elif gameData[3] == 2:
        print(f"[*] X's turn: {current_port}")
    elif gameData[3] == 3:
        print("[*] Cat's game...")
    elif gameData[3] == 4:
        print("[*] O wins!")
    elif gameData[3] == 5:
        print("[*] X wins!")
    elif gameData[3] == 0:
        print(f"[*] Game start!")
    else:
        print("[*] displayDiagnostics ERROR")
    print(f"[*] Send count: {gameData[2]}")
    printGameBoard(gameData[4:])


# global game data for both clients
gameData = [0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
players = [1, 0, 0]  # [current player], [player 1's current_port], [player 2's current_port]


# Listen for connections
def main():
    # make a TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((IP, current_port))
        # we don't need a large backlog (5)
        server.listen(5)
        print(f'[*] Listening on {IP}:{current_port}')

        # Continuously listen for clients from any address (0.0.0.0)
        while True:
            # Get the client
            client, address = server.accept()
            # print(f'[*] Accepted connection from {address[0]}:{address[1]}')

            # Here is the function call:
            client_handler = threading.Thread(target=handle_client, args=(client, address[0], address[1]))
            client_handler.start()
    except OSError as os:
        print("[*] OSError: Address already in use.")
    except KeyboardInterrupt as ki:
        print("\n[*] Exiting...")
    

# Send data back to the connecting client:
def handle_client(client_socket, address, current_port):
    with client_socket as sock:
        try:
            print(f'[*] Accepted connection from {address}:{current_port}')

            # use this to manage when to update the GUI on the server's side
            game_has_changed = True

            # store the current_port of each player
            if players[1] == 0:
                players[1] = current_port
                # convert data to a format that can be sent through a socket
                client_setup = ','.join(map(str, [3, 3, 1]))
                # send the data
                sock.send(client_setup.encode())
                gameData[2] += 1
            elif players[2] == 0 and players[1] != current_port:
                players[2] = current_port
                # convert data to a format that can be sent through a socket
                client_setup = ','.join(map(str, [3, 3, 2]))
                # send the data
                sock.send(client_setup.encode())
                gameData[2] += 1
            else:
                print("[*] Spaces full. No more players may join.")
                # convert data to a format that can be sent through a socket
                client_setup = ','.join(map(str, [3, 3, 0]))
                # send the data
                sock.send(client_setup.encode())
                gameData[2] += 1

            while True:

                time.sleep(1)

                if game_has_changed:
                    displayDiagnostics(gameData, current_port)

                # if game is over
                if gameData[3] > 2:

                    # convert data to a format that can be sent through a socket
                    gameDataStr = ','.join(map(str, gameData))
                    # send the data
                    sock.send(gameDataStr.encode())
                    gameData[2] += 1

                    # reset the game information but keep send-count
                    print(f"[*] Game data before reset: {gameData}")
                    print(f"[*] Players: {players}")
                    gameData[4:] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    print(f"[*] Game data after reset:  {gameData}")
                    gameData[3] = 1
                    players[0] = 1
                    players[1] = 0
                    players[2] = 0
                    break

                if gameData[3] == 0:
                    gameData[3] = 1

                # convert data to a format that can be sent through a socket
                gameDataStr = ','.join(map(str, gameData))
                # send the data
                sock.send(gameDataStr.encode())
                gameData[2] += 1

                # if the correct player has the current port
                if players[players[0]] == current_port:

                    # get the game data from client
                    received_data = sock.recv(1024)
                    gameData[2] += 1
                    response_raw = received_data.decode()
                    client_request = list(map(int, response_raw.split(',')))

                    # client move request type
                    if client_request[0] == 2:

                        # if the expected player's current_port is the current current_port, continue
                        if players[players[0]] == current_port:

                            # check to see if the requested spot is available
                            requested_spot = 3 + client_request[2]
                            if gameData[requested_spot] == 0:

                                # X's Turn
                                if players[0] == 1:
                                    other_player_turn = 2

                                # O's Turn
                                elif players[0] == 2:
                                    other_player_turn = 1

                                else:
                                    print("[*] CURRENT PLAYER CHECK ERROR")

                                # commit client's turn
                                gameData[requested_spot] = players[0]  # the piece for the player: X/O
                                game_has_changed = True

                                # computer turn
                                '''
                                if not isGameOver(gameData):
                                    # X's turn attempted
                                    gameData[3] = 2
                                    computerTurn(gameData)
                                displayDiagnostics(gameData, current_port)
                                '''

                                # game over? (this check can also change the value of the game state)
                                if isGameOver(gameData):

                                    displayDiagnostics(gameData, current_port)

                                    # convert data to a format that can be sent through a socket
                                    gameDataStr = ','.join(map(str, gameData))

                                    # send the data
                                    sock.send(gameDataStr.encode())
                                    gameData[2] += 1

                                # game is still going
                                else:
                                    gameData[3] = other_player_turn
                                    players[0] = other_player_turn

                            # correct player attempting to move in a filled space
                            else:
                                game_has_changed = False
                                print("[*] Client requested an occupied space.")

                        # wrong player attempting to move
                        else:
                            game_has_changed = False
                            print(f"[*] Wrong player attempted to move: {current_port}")

                    # type terminate game type
                    elif client_request[0] == 1:
                        print(f"[*] Disconnected from {address}:{current_port}")
                        for i in range(0, 1):
                            if players[i] == current_port:
                                players[i] = 0
                        break

                    else:
                        game_has_changed = False

                else:
                    game_has_changed = False

        except ValueError as ve:
            print("[*] ValueError: ", format(ve.args[0]))
            print("[*] Disconnected.")
        except KeyboardInterrupt as ki:
            print("\n[*] Exiting...")
        except ConnectionResetError as cre:
            print("[*] ConnectionResetError.")
        except BrokenPipeError as bp:
            print(f"[*] Disconnected from {address}:{current_port}")

        if gameData[3] <= 2:
            if players[1] == current_port:
                players[1] = 0
            elif players[2] == current_port:
                players[2] = 0

        print(f"[*] Players: {players}")


# START
if __name__ == '__main__':
    main()  
    

