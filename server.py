# TicTacToe Server
# Kyle Winfield Burnham
# 2023

# Black Hat Python by Justin Seitz and Tim Arnold
# https://learning.oreilly.com/library/view/black-hat-python/9781098128906/c02.xhtml#h1-501126c02-0004

import socket
import json
import threading
import random
import time

# What IP I am listening to:
server_IPv4 = '0.0.0.0'
# What current_port I am listening on:
server_port = 10101

# global game data for both clients
gameData = [0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
players = [1, 0, 0]  # [current player], [player 1's current_port], [player 2's current_port]

# CONSTANTS
COMPUTER_FILL_IN_TIMER = 15


# this checks to see if the game is over AND edits the value of the global variable 'gameData'
def isGameOver(data):
    gameBoard = data[4:]
    win_conditions = [
        # Rows
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        # Columns
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        # Diagonals
        [0, 4, 8], [2, 4, 6]
    ]

    if 0 not in gameBoard:
        data[3] = 3
        return True  # It's a draw, all spaces are filled
    for condition in win_conditions:
        a, b, c = condition
        if gameBoard[a] == gameBoard[b] == gameBoard[c] == 1:
            data[3] = 4
            return True  # O has won
        if gameBoard[a] == gameBoard[b] == gameBoard[c] == 2:
            data[3] = 5
            return True  # X has won

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


# run this function when there are no other players
def computerTurn(data):
    print("[*] Computer is taking a turn...")
    empty_spots = [i for i in range(9) if data[i + 4] == 0]

    # Check for winning moves
    for spot in empty_spots:
        temp_game_data = data.copy()
        temp_game_data[4 + spot] = players[0]
        if isGameOver(temp_game_data):
            data[4 + spot] = players[0]
            data[3] = 3 - players[0]
            players[0] = 3 - players[0]
            return

    # Check for blocking opponent's winning moves
    for spot in empty_spots:
        temp_game_data = data.copy()
        temp_game_data[4 + spot] = 3 - players[0]
        if isGameOver(temp_game_data):
            data[4 + spot] = players[0]
            data[3] = 3 - players[0]
            players[0] = 3 - players[0]
            return

    # If no winning or blocking moves, choose a random empty spot
    if empty_spots:
        computer_choice = random.choice(empty_spots)
        data[4 + computer_choice] = players[0]
        data[3] = 3 - players[0]
        players[0] = 3 - players[0]
    else:
        print("[*] Computer has no moves to take.")


# debugging on the server console
def displayDiagnostics(data, port):
    # print the game data
    print(f"[*] Players: {players}")
    if data[3] == 1:
        print(f"[*] O's turn: {port}")
    elif data[3] == 2:
        print(f"[*] X's turn: {port}")
    elif data[3] == 3:
        print("[*] Cat's game...")
    elif data[3] == 4:
        print("[*] O wins!")
    elif data[3] == 5:
        print("[*] X wins!")
    elif data[3] == 0:
        print(f"[*] Game start!")
    else:
        print("[*] displayDiagnostics ERROR")
    print(f" -  Send count: {data[2]}")
    printGameBoard(data[4:])


# Listen for connections
def main():
    # make a TCP server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((server_IPv4, server_port))
        # we don't need a large backlog (5)
        server.listen(5)
        print(f'[*] Listening on {server_IPv4}:{server_port}')

        # Continuously listen for clients from any address (0.0.0.0)
        while True:
            # Get the client
            client, address = server.accept()
            # print(f'[*] Accepted connection from {address[0]}:{address[1]}')

            # Here is the function call:
            client_handler = threading.Thread(target=handle_client, args=(client, address[0], address[1]))
            client_handler.start()
    except OSError:
        print("[*] OSError: Address already in use.")
    except KeyboardInterrupt:
        print("\n[*] Exiting...")


# Send data back to the connecting client:
def handle_client(client_socket, address, current_port):
    with client_socket as sock:
        try:
            print(f'[*] Accepted connection from {address}:{current_port}')

            # use this to manage when to update the GUI on the server's side
            game_has_changed = True
            time_until_computer_moves = COMPUTER_FILL_IN_TIMER

            # store the current_port of each player
            if players[1] == 0:
                players[1] = current_port
                # convert data to a format that can be sent through a socket
                client_setup = json.dumps([3, 3, 1])
                # send the data
                sock.send(client_setup.encode())
                gameData[2] += 1
            elif players[2] == 0 and players[1] != current_port:
                players[2] = current_port
                # convert data to a format that can be sent through a socket
                client_setup = json.dumps([3, 3, 2])
                # send the data
                sock.send(client_setup.encode())
                gameData[2] += 1
            else:
                print("[*] Spaces full. No more players may join.")
                # convert data to a format that can be sent through a socket
                client_setup = json.dumps([3, 3, 0])
                # send the data
                sock.send(client_setup.encode())
                gameData[2] += 1

            while True:

                # # # # #                         # # # # #
                # # # #                             # # # #
                # # # \/ IMPORTANT : DO NOT DELETE \/ # # #
                # #                                     # #
                #                                         #
                time.sleep(1)  # <-- MAINTAINS FLOW-CONTROL
                #                                         #
                # #                                     # #
                # # # /\ IMPORTANT : DO NOT DELETE /\ # # #
                # # # #                             # # # #
                # # # # #                         # # # # #

                if game_has_changed:
                    displayDiagnostics(gameData, current_port)

                # if game is over
                if gameData[3] > 2:

                    # convert data to a format that can be sent through a socket
                    gameDataFormatted = json.dumps(gameData)
                    # send the data
                    sock.send(gameDataFormatted.encode())
                    gameData[2] += 1

                    # reset the game
                    gameData[3] = 1
                    players[0] = 1

                    # reset the players
                    players[1] = 0
                    players[2] = 0
                    break

                if gameData[3] == 0:
                    gameData[3] = 1

                # if it's their turn
                if players[players[0]] == current_port:

                    # convert data to a format that can be sent through a socket
                    gameDataFormatted = json.dumps(gameData)
                    # send the data
                    sock.send(gameDataFormatted.encode())
                    gameData[2] += 1

                    # listen to the client
                    received_data = sock.recv(1024)
                    gameData[2] += 1
                    client_request = json.loads(received_data.decode())

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

                                # game over? (this check can also change the value of the game state)
                                if isGameOver(gameData):

                                    displayDiagnostics(gameData, current_port)

                                    # convert data to a format that can be sent through a socket
                                    gameDataFormatted = json.dumps(gameData)

                                    # send the data
                                    sock.send(gameDataFormatted.encode())
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
                        print(f"f[*] Received a bad type protocol from {address}:{current_port}")
                        game_has_changed = False

                # if it's not their turn
                else:

                    # update the client's game once after they move so that they see their own move
                    if game_has_changed:
                        # tell the client that the computer is filling in
                        gameDataFormatted = json.dumps(gameData)
                        # send the data
                        sock.send(gameDataFormatted.encode())
                        gameData[2] += 1

                    # after updating client's game data, count down to filling in as computer
                    else:

                        # if there's only one player currently
                        if 0 in players:

                            # a computer will play instead of a player if a player doesn't connect for 10 seconds
                            if time_until_computer_moves == COMPUTER_FILL_IN_TIMER:
                                print("[*] Looking for opponent...")
                            if time_until_computer_moves != COMPUTER_FILL_IN_TIMER and time_until_computer_moves % 5 == 0:
                                print(f"[*] Time until computer makes a move: {time_until_computer_moves}")
                            time_until_computer_moves -= 1

                            # if it has been 10 seconds with no opponent
                            if time_until_computer_moves <= 0:

                                # Take computer's turn
                                computerTurn(gameData)

                                # tell the client that the computer is filling in
                                matchmaking_diagnostics = json.dumps([4, 3, 2])
                                # send the data
                                sock.send(matchmaking_diagnostics.encode())
                                gameData[2] += 1

                                # game over? (this check can also change the value of the game state)
                                if isGameOver(gameData):
                                    displayDiagnostics(gameData, current_port)
                            else:
                                # tell the client that the opponent is disconnected
                                matchmaking_diagnostics = json.dumps([4, 3, 0])
                                # send the data
                                sock.send(matchmaking_diagnostics.encode())
                                gameData[2] += 1
                        else:
                            time_until_computer_moves = COMPUTER_FILL_IN_TIMER
                            # tell the client that the opponent is disconnected
                            matchmaking_diagnostics = json.dumps([4, 3, 1])
                            # send the data
                            sock.send(matchmaking_diagnostics.encode())
                            gameData[2] += 1

                    # after one loop, don't keep updating if the game hasn't updated
                    game_has_changed = False

        except ValueError as ve:
            print("[*] ValueError: ", format(ve.args[0]))
            print(f" -  Disconnected from {address}:{current_port}")
        except KeyboardInterrupt:
            print("\n[*] Exiting...")
        except ConnectionResetError:
            print("[*] ConnectionResetError.")
        except BrokenPipeError:
            print(f"[*] Disconnected from {address}:{current_port}")
        except IndexError:
            print(f"[*] IndexError")
            print(f" -  Disconnected from {address}:{current_port}")

        if gameData[3] <= 2:
            if players[1] == current_port:
                players[1] = 0
            elif players[2] == current_port:
                players[2] = 0

        print(f"[*] Players: {players}")

        # reset the game if there are no players
        if players[1] == 0 and players[2] == 0:
            # reset the game information but keep send-count
            print(f"[*] Game data before reset: {gameData}")
            print(f" -  Players: {players}")
            gameData[4:] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            # reset send count to avoid reaching unreasonably high numbers
            if gameData[2] > 999:
                gameData[2] = 1
            print(f" -  Game data after reset:  {gameData}")
            gameData[3] = 1
            players[0] = 1


# START
if __name__ == '__main__':
    main()
