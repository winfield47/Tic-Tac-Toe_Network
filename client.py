# TicTacToe Client
# Kyle Winfield Burnham
# 2023

# Black Hat Python by Justin Seitz and Tim Arnold
# https://learning.oreilly.com/library/view/black-hat-python/9781098128906/c02.xhtml#h1-501126c02-0003

import socket
import json
import random
import time
import os


def get_target_address():
    # Set the default IPv4 address
    default_address = "127.0.0.1"

    try:
        # Prompt the user for an IPv4 address
        user_input = input(f"Please enter a TicTacToe IPv4 address to connect to.\n(Default: {default_address}): ")

        # Use the entered address if provided, otherwise use the default
        target_address = user_input.strip() if user_input.strip() else default_address

        # Validate the entered IPv4 address
        socket.inet_pton(socket.AF_INET, target_address)

        # Return the validated or default address
        return target_address

    except ValueError:
        # Handle the case where the entered address is not a valid IPv4 address
        print("Invalid IPv4 address.\nUsing the default address.")
        time.sleep(3)
        return default_address

    except socket.error as e:
        print(f"Socket error: {e}.\nUsing the default address.")
        time.sleep(3)
        return default_address

    except Exception as e:
        print(f"An unexpected error occurred: {e}.\nUsing the default address.")
        time.sleep(3)
        return default_address

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")


def clear_input_buffer():
    try:
        import msvcrt  # for Windows
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys
        import termios  # for Linux/macOS
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


def displayWhoWon(data, client_piece):
    if data[3] == 3:
        print("Cat's game...")
    elif data[3] == 4:
        if convertSpotValue(client_piece) == 'O':
            print("You won!")
        else:
            print("You lost!")
    elif data[3] == 5:
        if convertSpotValue(client_piece) == 'X':
            print("You won!")
        else:
            print("You lost!")
    else:
        print(f"displayWhoWon ERROR:\nGame Data:{data}")


def convertSpotValue(spot):
    if spot == 0:
        return " "
    if spot == 1:
        return "O"
    if spot == 2:
        return "X"
    else:
        return "E"


def printGameBoard(spots, place=0):
    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    # authenticate the quality of the data in spots
    # ignore bad data
    if 13 not in spots:  # 13 in spots means that all the gameData was given: this is bad
        # then print the board
        print("Current Game: ")
        print("+---+---+---+")
        count = 0
        for spot in spots:
            count += 1
            # display the numbers for each space slowly
            # print the spot
            print("| " + (str(place) if (count == place and spot == 0) else convertSpotValue(spot)), end=" ")
            if count % 3 == 0:
                print(f"| <- {count - 2}, {count - 1}, {count}\n+---+---+---+")

    clear_input_buffer()


def getTurn():
    while True:
        try:
            choice = int(input("Choice: "))
            if 1 <= choice <= 9:
                return choice
            else:
                print("Invalid choice. Please choose a number between 1 and 9.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def main():

    # IPv4 I want to connect to:
    target_address = get_target_address()
    # Port I want to connect to:
    target_port = 10101

    # TicTacToe
    continueKey = 'y'
    try:

        while continueKey.lower() == 'y' or continueKey == '':

            # create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect the client
            client_socket.connect((target_address, target_port))
            print(f"[*] Connected to {target_address}:{target_port}")

            # base data for gameData
            gameData = [0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            myTurn = 0
            moveWasJustSent = False
            numerical_space = 1
            needs_tutorial = False
            computer_is_playing = False
            opponent_is_connected = False

            while True:

                # print("waiting for response...")
                # receive some data
                server_response = client_socket.recv(4096)
                # print what was sent to us from the server we connected to
                server_response = json.loads(server_response.decode())

                # initialize the data i need to send
                request = [2, 3, 0]  # 0 is a placeholder

                # server updating our game
                if server_response[0] == 0:

                    # authenticate that the data is of good quality
                    if server_response[1] == 13:

                        # authenticate that the send-count is bigger than last time
                        if server_response[2] > gameData[2]:
                            gameData = server_response

                            # if it's my turn currently
                            if gameData[3] == myTurn:
                                # Take a Turn!
                                printGameBoard(gameData[4:])

                                # this should only be True here if the input wasn't accepted by the server
                                # and THAT is only when the spot has been taken already
                                print(f"Your turn! -> '{convertSpotValue(myTurn)}'")
                                if opponent_is_connected:
                                    print("VS. Player")
                                elif computer_is_playing:
                                    print("VS. Computer")
                                if moveWasJustSent:
                                    print("That spot is taken!")
                                if needs_tutorial:
                                    print("Spots go from left to right, then top to bottom:")
                                    print("\tEx: 1 -> top left")
                                    print("\tEx: 5 -> middle")
                                    print("\tEx: 9 -> bottom right")
                                    needs_tutorial = False

                                # take your turn
                                request[2] = getTurn()

                                # convert data to a format that can be sent through a socket
                                request = json.dumps(request)
                                # send the data
                                client_socket.send(request.encode())

                                moveWasJustSent = True

                            # if it's the opponent's turn currently
                            elif gameData[3] == 3 - myTurn:

                                # just print the board, nothing fancy
                                printGameBoard(gameData[4:])
                                print(f"You are playing as '{convertSpotValue(myTurn)}'")

                                '''
                                # display the number for each space one by one
                                if numerical_space > 9:
                                    numerical_space = 1

                                while gameData[3 + numerical_space] != 0:
                                    numerical_space += 1
                                    if numerical_space > 9:
                                        numerical_space = 1

                                # display the current board
                                if computer_is_playing:
                                    printGameBoard(gameData[4:])
                                    print(f"You are playing as '{convertSpotValue(myTurn)}'")
                                    print("Computer is thinking...")
                                    moveWasJustSent = False
                                else:
                                    printGameBoard(gameData[4:], numerical_space)
                                    print(f"You are playing as '{convertSpotValue(myTurn)}'")
                                    print("Waiting for opponent...")
                                    if not moveWasJustSent:
                                        print("(Computer plays for absent opponents.)")
                                    moveWasJustSent = False
                                    numerical_space += 1
                                '''

                            # if the game is over
                            if gameData[3] >= 3:
                                # leave the loop
                                break

                # inform the client on which piece they will be using
                elif server_response[0] == 3:
                    myTurn = server_response[2]
                    # too many players
                    if server_response[2] == 0:
                        print("Game already has 2 players.")
                        print("Try again later...")

                        # tell the server that we are done playing
                        msg = json.dumps([1, 2])
                        client_socket.send(msg.encode())

                        # Close the client nicely
                        client_socket.close()

                        return

                    # player is O
                    elif server_response[2] == 1:
                        print("Your piece will be O.")
                        time.sleep(1)
                        needs_tutorial = True

                    # player is X
                    elif server_response[2] == 2:
                        print("Your piece will be X.")
                        time.sleep(1)
                        printGameBoard(gameData[4:], 1)
                        print(f"You are playing as '{convertSpotValue(myTurn)}'")
                        print("Waiting for opponent...")
                        needs_tutorial = True

                    # if the server sends bad data
                    else:
                        print("ERROR: Server sent bad data...")
                        print(f"DATA SENT: {server_response}")

                        # tell the server that we are done playing
                        msg = json.dumps([1, 2])
                        client_socket.send(msg.encode())

                        # Close the client nicely
                        client_socket.close()

                        return

                # matchmaking updates
                elif server_response[0] == 4:

                    # validate quality of data
                    if server_response[1] == 3:

                        # if opponent is disconnected
                        if server_response[2] == 0:

                            # display the number for each space one by one
                            if numerical_space > 9:
                                numerical_space = 1

                            while gameData[3 + numerical_space] != 0:
                                numerical_space += 1
                                if numerical_space > 9:
                                    numerical_space = 1

                            # display the current board
                            printGameBoard(gameData[4:], numerical_space)
                            print(f"You are playing as '{convertSpotValue(myTurn)}'")
                            if opponent_is_connected:
                                print("Opponent disconnected!")
                            else:
                                print("Looking for opponent...")
                                print("After some time, if an opponent is not found, a computer will fill in.")
                            computer_is_playing = False
                            opponent_is_connected = False
                            moveWasJustSent = False
                            numerical_space += 1

                        # if opponent is connected
                        if server_response[2] == 1:

                            # display the number for each space one by one
                            if numerical_space > 9:
                                numerical_space = 1

                            while gameData[3 + numerical_space] != 0:
                                numerical_space += 1
                                if numerical_space > 9:
                                    numerical_space = 1

                            # display the current board
                            printGameBoard(gameData[4:], numerical_space)
                            print(f"You are playing as '{convertSpotValue(myTurn)}'")

                            if opponent_is_connected:
                                print("Waiting on opponent's move...")
                            else:
                                print("Found a player!")
                            computer_is_playing = False
                            opponent_is_connected = True
                            moveWasJustSent = False
                            numerical_space += 1

                        # if computer is filling in for opponent
                        if server_response[2] == 2:

                            # display the current board
                            printGameBoard(gameData[4:])
                            print(f"You are playing as '{convertSpotValue(myTurn)}'")
                            if not computer_is_playing:
                                print("Computer is filling in...")
                            else:
                                print("Computer is thinking...")
                            computer_is_playing = True
                            opponent_is_connected = False
                            moveWasJustSent = False

            printGameBoard(gameData[4:])
            displayWhoWon(gameData, myTurn)
            print("Game over!")

            time.sleep(1)

            # tell the server that we are done playing
            msg = json.dumps([1, 2])
            client_socket.send(msg.encode())
            # Close the client nicely
            client_socket.close()
            continueKey = input("Continue playing? (Y/n)?: ")

    except KeyboardInterrupt:
        print("\n[*] Exiting...")

    except ConnectionRefusedError as cre:
        print("ConnectionRefusedError: ", format(cre.args[0]))
        print("It's possible the IPv4 Address you entered is incorrect.\nTry using: 127.0.0.1")

    except ValueError as ve:
        print("ValueError: ", format(ve.args[0]))

    except TypeError:
        print("\n[*] Exiting...")

    # clear the screen
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()
