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


# CONSTANTS
TUTORIAL_FILE_PATH = "tutorial_seen.txt"
TUTORIAL_CHAR = 'n'


def get_target_address():
    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
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
        # clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        # Handle the case where the entered address is not a valid IPv4 address
        print("Invalid IPv4 address.")
        time.sleep(1)
        print("Using the default address.")
        time.sleep(1)
        return default_address

    except socket.error as e:
        # clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Socket error: {e}.")
        time.sleep(1)
        print(f"Using the default address.")
        time.sleep(1)
        return default_address

    except Exception as e:
        # clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"An unexpected error occurred: {e}.")
        time.sleep(1)
        print("Using the default address.")
        time.sleep(1)
        return default_address

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
        return -1
    except EOFError:
        print("\nEOF")
        return -1


# get a server port to be able to host multiple games
def get_target_port():
    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    # Set the default port
    default_port = 10101

    while True:
        try:
            # Prompt the user for a port number
            user_input = input(f"Please enter the port number to connect to.\n(Default: {default_port}): ")

            # Use the entered port if provided, otherwise use the default
            port = int(user_input) if user_input.strip() else default_port

            # Validate the entered port number
            if 0 < port < 65535:
                return port
            else:
                # clear the screen
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Invalid port number.")
                time.sleep(1)
                print("Using the default port.")
                time.sleep(1)
                return default_port

        except ValueError:
            # clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Invalid input.")
            time.sleep(1)
            print("Using the default port.")
            time.sleep(1)
            return default_port

        except KeyboardInterrupt:
            print("\nKeyboardInterrupt")
            return -1
        except EOFError:
            print("\nEOF")
            return -1


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


def getContinueKey():
    try:
        return input("Continue playing? (Y/n)?: ")
    except KeyboardInterrupt:
        return 'n'


def getTurn(player_piece):
    print(f"You are playing as '{convertSpotValue(player_piece)}'")
    return input("Choice: ")


def printYourTurn():
    print("^ YOUR TURN ^")


def doesPlayerNeedTutorial():
    content = ""
    try:
        # check to see if the file exists
        try:
            with open(TUTORIAL_FILE_PATH, 'r') as file:
                content = file.read().strip().lower()
        except FileNotFoundError:
            pass
        if content == TUTORIAL_CHAR:
            return True if input("Is this your first time using this program? (y/N): ").lower() == 'y' else False
        else:
            return False if input("Is this your first time using this program? (Y/n): ").lower() == 'n' else True
    except KeyboardInterrupt:
        return -1
    except EOFError:
        return -1


def printTutorial(player_piece):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("\t\t[*] MULTIPLAYER TICTACTOE TUTORIAL [*]")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(f"[*] The server has assigned you the '{convertSpotValue(player_piece)}' piece!")
    print("[*] To place this piece, type in the spot you'd like to place it in!")
    print("[*] Spots go from left to right, then top to bottom:")
    print("   -  Ex: 1 -> top left spot")
    print("   -  Ex: 5 -> middle spot")
    print("   -  Ex: 9 -> bottom right spot")
    print("[*] Before (or after) entering your move, please connect another")
    print("    client as your opponent, using the default connections.")
    print("[*] If you don't connect another client, then after a short time")
    print("    a computer will be matched against you (decent AI).")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    # Write the user's choice to the file
    with open(TUTORIAL_FILE_PATH, 'w') as file:
        file.write(TUTORIAL_CHAR)


def update_numerical_space(num_space, spots):

    # display the number for each space one by one
    if num_space > 9:
        num_space = 0

    # skip all spots with pieces in them
    if num_space != 0:
        while spots[num_space - 1] != 0:  # this checks every spot on the board
            num_space += 1
            if num_space > 9:
                num_space = 0
                break

    return num_space


def printGameBoard(spots, opp_connected, comp_connected, num_space=0):
    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
    # authenticate the quality of the data in spots
    # ignore bad data
    if 13 not in spots:  # 13 in spots means that all the gameData was given, which is bad
        # then print the board
        if opp_connected:
            print("TicTacToe: You VS Player")
        elif comp_connected:
            print("TicTacToe: You VS Computer")
        else:
            print("TicTacToe: Looking for opponent...")
        print("+---+---+---+")
        count = 0
        # find out if multiple spaces are open
        empty_spaces = 0
        for spot in spots:
            if spot == 0:
                empty_spaces += 1
        for spot in spots:
            count += 1
            if count == num_space and spot == 0:
                # make sure there are multiple spaces open
                if empty_spaces == 1:
                    # display the numbers for each space slowly
                    print("| " + convertSpotValue(spot), end=" ")
                else:
                    # display the numbers for each space slowly
                    print("| " + str(num_space), end=" ")
            else:
                # print the spot
                print("| " + convertSpotValue(spot), end=" ")
            if count % 3 == 0:
                print(f"| <- {count - 2}, {count - 1}, {count}\n+---+---+---+")

    clear_input_buffer()


def main():

    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # is the player new to my program?
    needs_tutorial = doesPlayerNeedTutorial()

    # make sure the server is running
    server_is_running = False

    # if the user keyboard-interrupts
    if needs_tutorial == -1:
        # clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    # don't scare away the noobs!
    if needs_tutorial:
        target_address = "127.0.0.1"
        target_port = 10101

    # let the veterans do what they want
    else:
        # IPv4 I want to connect to:
        target_address = get_target_address()

        # if the user keyboard-interrupts
        if target_address == -1:
            # clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            return

        # Port I want to connect to:
        target_port = get_target_port()

        # if the user keyboard-interrupts
        if target_port == -1:
            # clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            return

    # TicTacToe
    continueKey = 'y'
    try:

        # loop once per game
        while continueKey.lower() == 'y' or continueKey == '':

            # create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect the client
            client_socket.connect((target_address, target_port))
            # clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"[*] Connected to {target_address}:{target_port}")
            server_is_running = True

            # base data for gameData
            gameData = [0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            myTurn = 0
            moveWasJustSent = False
            numerical_space = 1
            computer_is_playing = False
            opponent_is_connected = False

            # loop every time we get a server message
            while True:

                # receive some data
                server_response = client_socket.recv(4096)
                # print what was sent to us from the server we connected to
                server_response = json.loads(server_response.decode())

                # initialize the data i need to send
                request = [2, 3, 0]  # 0 is a placeholder

                #
                # # server updating our game
                #
                if server_response[0] == 0:

                    # authenticate that the data is of good quality
                    if server_response[1] == 13:

                        # authenticate that the send-count is bigger than last time
                        if server_response[2] > gameData[2]:
                            gameData = server_response

                            # if it's my turn currently
                            if gameData[3] == myTurn:
                                # Take a Turn!
                                printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
                                printYourTurn()
                                if moveWasJustSent:
                                    print("That spot is taken!")
                                if needs_tutorial:
                                    printTutorial(myTurn)
                                    needs_tutorial = False

                                # take your turn
                                request[2] = getTurn(myTurn)

                                # convert data to a format that can be sent through a socket
                                request = json.dumps(request)
                                # send the data
                                client_socket.send(request.encode())

                                moveWasJustSent = True

                            # if it's the opponent's turn currently
                            elif gameData[3] == 3 - myTurn:

                                # just print the board, nothing fancy
                                printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
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

                #
                # # inform the client on which piece they will be using
                #
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
                        print("Loading the game...")
                        time.sleep(1)

                    # player is X
                    elif server_response[2] == 2:
                        printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
                        print(f"You are playing as '{convertSpotValue(myTurn)}'")
                        print("Waiting for opponent...")

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

                #
                # # matchmaking updates
                #
                elif server_response[0] == 4:

                    # validate quality of data
                    if server_response[1] == 3:

                        # if opponent is disconnected
                        if server_response[2] == 0:

                            # make a number show in all the spots one at a time
                            numerical_space = 0 if moveWasJustSent else numerical_space
                            numerical_space = update_numerical_space(numerical_space, gameData[4:])

                            # display the current board
                            printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing, numerical_space)
                            print(f"You are playing as '{convertSpotValue(myTurn)}'")
                            if opponent_is_connected:
                                print("Opponent disconnected!")
                            else:
                                print("If an opponent is not found soon, a computer will fill in.")
                            computer_is_playing = False
                            opponent_is_connected = False
                            moveWasJustSent = False
                            numerical_space += 1

                        # if opponent is connected
                        if server_response[2] == 1:

                            # make a number show in all the spots one at a time
                            numerical_space = 0 if moveWasJustSent else numerical_space
                            numerical_space = update_numerical_space(numerical_space, gameData[4:])

                            # display the current board
                            printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing, numerical_space)
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
                            printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
                            print(f"You are playing as '{convertSpotValue(myTurn)}'")
                            if not computer_is_playing:
                                print("Computer is filling in...")
                            else:
                                print("Computer is thinking...")
                            computer_is_playing = True
                            opponent_is_connected = False
                            moveWasJustSent = False

                #
                # # inform the client of their bad input
                #
                elif server_response[0] == 5:

                    # validate quality of data
                    if server_response[1] == 3:

                        # client gave goggly-guk
                        if server_response[2] == 0:

                            # Take a Turn!
                            printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
                            printYourTurn()

                            print("Invalid input. Please enter a number.")

                            # take your turn
                            request[2] = getTurn(myTurn)

                            # convert data to a format that can be sent through a socket
                            request = json.dumps(request)
                            # send the data
                            client_socket.send(request.encode())

                            moveWasJustSent = True

                        # client input is out-of-range
                        if server_response[2] == 1:

                            # Take a Turn!
                            printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
                            printYourTurn()
                            if moveWasJustSent:
                                print("Invalid choice. Please choose a number between 1 and 9.")

                            # take your turn
                            request[2] = getTurn(myTurn)

                            # convert data to a format that can be sent through a socket
                            request = json.dumps(request)
                            # send the data
                            client_socket.send(request.encode())

                            moveWasJustSent = True

                        # spot is taken!
                        if server_response[2] == 2:

                            # Take a Turn!
                            printGameBoard(gameData[4:], opponent_is_connected, computer_is_playing)
                            printYourTurn()
                            if moveWasJustSent:
                                print("That spot is taken!")

                            # take your turn
                            request[2] = getTurn(myTurn)

                            # convert data to a format that can be sent through a socket
                            request = json.dumps(request)
                            # send the data
                            client_socket.send(request.encode())

                            moveWasJustSent = True

            printGameBoard(gameData[4:], computer_is_playing, opponent_is_connected)
            print("^ GAME OVER ^")
            displayWhoWon(gameData, myTurn)

            time.sleep(1)

            # tell the server that we are done playing
            msg = json.dumps([1, 2])
            client_socket.send(msg.encode())
            # Close the client nicely
            client_socket.close()
            continueKey = getContinueKey()

    except KeyboardInterrupt:
        print("\n[*] Exiting...")

    except EOFError:
        print("\n[*] Exiting...")

    except ConnectionRefusedError as cre:
        print("No connection...")
        pass

    except ValueError as ve:
        print("ValueError: ", format(ve.args[0]))

    except TypeError:
        print("\n[*] Exiting...")

    # clear the screen
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')

    # if they don't know what they did wrong
    if not server_is_running:
        print("[*] The TicTacToe server is most likely not running.")
        print("[*] You also may have entered in the wrong address or port.")
        print("[*] In another terminal window, try running: python server.py")
        print("[*] Then, use the default server port.")


if __name__ == "__main__":
    main()
