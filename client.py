# TicTacToe Client
# Kyle Winfield Burnham

# Black Hat Python by Justin Seitz and Tim Arnold
# https://learning.oreilly.com/library/view/black-hat-python/9781098128906/c02.xhtml#h1-501126c02-0003

import socket
import random


def displayWhoWon(gameData):
    if gameData[3] == 3:
        print("Cat's game...")
    elif gameData[3] == 4:
        print("O wins!")
    elif gameData[3] == 5:
        print("X wins!")
    else:
        print("ERROR")


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


def takeTurn(gameData):
    # Take a Turn!
    print("Please enter the position you'd like to place an 'O'\n(left to right, then top to bottom):")
    print("Ex: 1 -> top left")
    print("Ex: 5 -> middle")
    print("Ex: 9 -> bottom right")

    while True:
        try:
            choice = int(input("Choice: "))
            if 1 <= choice <= 9:
                if gameData[3 + choice] == 0:
                    gameData[3 + choice] = 1
                    gameData[3] = 1
                    break
                else:
                    print("Spot already occupied. Please choose an empty spot.")
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
    sendCount = 0
    continueKey = 'y'
    try:
        # create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect the client
        client_socket.connect((target_host, target_port))

        while continueKey.lower() == 'y' or continueKey == '':
            gameData = [0, 13, sendCount, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

            while True:

                if sendCount == 0:
                    print(f"[*] Connected to {target_host}:{target_port}")

                if gameData[0] == 0:

                    if gameData[1] == 13:

                        # show the board
                        printGameBoard(gameData[4:])

                        # take your turn
                        takeTurn(gameData)

                        # display turn taken
                        printGameBoard(gameData[4:])

                        # convert data to a format that can be sent through a socket
                        gameData[2] += 1
                        gameDataStr = ','.join(map(str, gameData))

                        # send the data
                        client_socket.send(gameDataStr.encode())

                # receive some data
                response = client_socket.recv(4096)

                # print what was sent to us from the server we connected to
                response = response.decode()
                serverGameData = list(map(int, response.split(',')))
                if serverGameData[2] == gameData[2] + 1:
                    gameData = serverGameData

                # if the game is over
                if gameData[3] != 1 and gameData[3] != 2:
                    # leave the loop
                    break

            displayWhoWon(gameData)

            sendCount = gameData[2]
            print("Game over!")
            continueKey = input("Continue playing? (Y/n)?: ")

        # tell the server that we are done playing
        msg = [1, 2]
        msg = ','.join(map(str, msg))
        client_socket.send(msg.encode())

        # Close the client nicely
        client_socket.close()

    except KeyboardInterrupt as ki:
        print("\n[*] Exiting...")
    except ConnectionRefusedError as cre:
        print("ConnectionRefusedError: ", format(cre.args[0]))
        if sendCount == 0:
            print("It's possible the IPv4 Address you entered is incorrect.\nTry using: 127.0.0.1")


if __name__ == "__main__":
    main()

