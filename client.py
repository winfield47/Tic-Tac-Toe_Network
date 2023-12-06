# TicTacToe Client
# Kyle Winfield Burnham

# Black Hat Python by Justin Seitz and Tim Arnold
# https://learning.oreilly.com/library/view/black-hat-python/9781098128906/c02.xhtml#h1-501126c02-0003

import socket
import random
import time
import os


def displayWhoWon(gameData):
    if gameData[3] == 3:
        print("Cat's game...")
    elif gameData[3] == 4:
        print("O wins!")
    elif gameData[3] == 5:
        print("X wins!")
    else:
        print(f"displayWhoWon ERROR:\nGame Data:{gameData}")


def convertSpotValue(spot):
    if spot == 0:
        return " "
    if spot == 1:
        return "O"
    if spot == 2:
        return "X"
    else:
        return "convertSpotValue ERROR: Bad spot value: " + str(spot)


def printGameBoard(spots, place=0):
    # clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')
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
            print(f"| <- {count - 2}-{count}\n+---+---+---+")


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

    user_input = input("Please enter a TicTacToe IPv4 address to connect to.\n(Default: 127.0.0.1): ")

    # IPv4 I want to connect to:
    target_host = "127.0.0.1" if user_input == "" else user_input
    # Port I want to connect to:
    target_port = 10101

    # TicTacToe
    continueKey = 'y'
    try:

        while continueKey.lower() == 'y' or continueKey == '':

            # create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect the client
            client_socket.connect((target_host, target_port))
            print(f"[*] Connected to {target_host}:{target_port}")

            # base data for gameData
            gameData = [0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            myTurn = 0
            moveWasJustSent = False
            numerical_space = 1
            needs_tutorial = False

            while True:

                # print("waiting for response...")
                # receive some data
                server_response = client_socket.recv(4096)
                # print what was sent to us from the server we connected to
                server_response = server_response.decode()
                # print(f"server response: {server_response}")
                server_response = list(map(int, server_response.split(',')))

                # initialize the data i need to send
                request = [2, 3, 0]  # 0 is a placeholder

                # server updating our game type
                if server_response[0] == 0:

                    # authenticate that the data is of good quality
                    if server_response[1] == 13:

                        # authenticate that the send-count is bigger than last time
                        if server_response[2] > gameData[2]:
                            gameData = server_response

                            # show the board
                            if gameData[3] == myTurn:
                                # Take a Turn!
                                printGameBoard(gameData[4:])

                                # this should only be True here if the input wasn't accepted by the server
                                if moveWasJustSent:
                                    print("That spot is taken!")
                                else:
                                    print(f"Your turn! -> '{convertSpotValue(myTurn)}'")
                                if needs_tutorial:
                                    print("Spots go from left to right, then top to bottom:")
                                    print("\tEx: 1 -> top left")
                                    print("\tEx: 5 -> middle")
                                    print("\tEx: 9 -> bottom right")
                                    needs_tutorial = False

                                # take your turn
                                request[2] = getTurn()

                                # convert data to a format that can be sent through a socket
                                request = ','.join(map(str, request))
                                # send the data
                                client_socket.send(request.encode())

                                moveWasJustSent = True

                            elif gameData[3] == 3 - myTurn:

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
                                print("Waiting for other player's move...")
                                moveWasJustSent = False
                                numerical_space += 1

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
                        msg = [1, 2]
                        msg = ','.join(map(str, msg))
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
                        print("Waiting for other player's move...")
                        needs_tutorial = True

                    # if the server sends bad data
                    else:
                        print("ERROR: Server sent bad data...")
                        print(f"DATA SENT: {server_response}")

                        # tell the server that we are done playing
                        msg = [1, 2]
                        msg = ','.join(map(str, msg))
                        client_socket.send(msg.encode())

                        # Close the client nicely
                        client_socket.close()

                        return

            displayWhoWon(gameData)
            printGameBoard(gameData[4:])
            print("Game over!")

            time.sleep(1)

            # tell the server that we are done playing
            msg = ','.join(map(str, [1, 2]))
            client_socket.send(msg.encode())
            # Close the client nicely
            client_socket.close()
            continueKey = input("Continue playing? (Y/n)?: ")

    except KeyboardInterrupt as ki:
        print("\n[*] Exiting...")

    except ConnectionRefusedError as cre:
        print("ConnectionRefusedError: ", format(cre.args[0]))
        print("It's possible the IPv4 Address you entered is incorrect.\nTry using: 127.0.0.1")


if __name__ == "__main__":
    main()

