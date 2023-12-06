# TicTacToe Library
# Kyle Winfield Burnham
import random


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

    for condition in win_conditions:
        a, b, c = condition
        if gameBoard[a] == gameBoard[b] == gameBoard[c] == 1:
            print("You win!")
            return True  # Player has won
        if gameBoard[a] == gameBoard[b] == gameBoard[c] == 2:
            print("You lose!")
            return True  # Computer has won
    if 0 not in gameBoard:
        print("Cat's game...")
        return True  # It's a draw, all spaces are filled

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


def takeTurn(gameData):
    # Take a Turn!
    print("Please enter the position you'd like to place an 'O'\n(left to right, then top to bottom):")
    print("Ex: 1 -> top left")
    print("Ex: 5 -> middle")
    print("Ex: 9 -> bottom right")

    while True:
        choice = input("Choice: ")
        position = int(choice)
        if position < 1 or position > 9:
            print("Invalid choice. Please choose a number between 1 and 9.")
        elif gameData[3 + position] != 0:
            print("Spot already occupied. Please choose an empty spot.")
        else:
            gameData[3 + position] = 1
            gameData[3] = 1
            break


def computerTurn(gameData):
    empty_spots = [i for i in range(9) if gameData[i + 4] == 0]
    if empty_spots:
        computer_choice = random.choice(empty_spots)
        gameData[4 + computer_choice] = 2  # Computer's move (2 for X)
        gameData[3] = 2
    else:
        print("It's a draw!")