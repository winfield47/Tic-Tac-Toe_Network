# Tic-Tac-Toe Protocol
### Layer 4 Protocol: 
- TCP
### Port: 
- 10101
### Client Game States:
- Waiting for Server Address
- Waiting for Turn Assignment
- Waiting for Player’s Input
- Waiting for Move Validation from Server
- Waiting for Game Update
- Game Over
- Waiting for User Input to Play Again or Disconnect
### Server Game States:
- Waiting for Connection from Client
- Waiting for Client to Move
- Approving Client’s Move
- Making a Computer Move
- Game Over
- Client <—> Server Messaging (Type Length Value) The Server will send the entire game information (Python list of Ints) to the Client. And the Client will send requests for the space they want to put their respective piece. Their pieces are assigned to them by the server.
## Type:
- Size of 1 int
  - Type 0 is the Tic-Tac-Toe game data protocol. This protocol sends the information of the game state to the clients.
  - Type 1 will be a terminating type. This tells the server that it’s time to end the connection. No data is necessary. Length will be 2.
  - Type 2 will be the turn request type. This protocol is sent by a client to a server and requests the move they want to take.
  - Type 3 will be for the server to communicate with the clients in order to give them information about which turn and piece they are.
  - Type 4 will be for the server to update the client on things that are going on around the game (i.e. opponents disconnecting, invalid moves, etc.).
  - Type 5 will be how the server tells the client about the status of their input request (i.e. when their request is random characters instead of a number from 1 to 9).
## Length:
- This will indicate how many integers are present in the data 
  - Type 0: 13 (1 integer tells the Type, 1 integer tells the Length, and 11 integers are left for the Value)
  - Type 1: 2 (1 for Type, 1 for Length, and NO values).
  - Type 2: 3 (1 for Type, 1 for Length, and 1 for Value).
  - Type 3: 3 (1 for Type, 1 for Length, and 1 for Value).
  - Type 4: 3 (1 for Type, 1 for Length, and 1 for Value).
  - Type 5: 3 (1 for Type, 1 for Length, and 1 for Value).
## Values:
### Type 0:
- Int 1: Send Count (How many communications have occurred since the connection. The Client/Server should make sure that the Turn Count it receives is always only 1 more than its lastly sent packet. Turn Count includes all forms of communications even when a “turn” isn’t necessarily being taken like when a game restarts into the Game Start Generic Gamestate [See below])
  - Value 0: Connection Start
  - Value {unsigned int}: Turns Occured
- Int 2: Generic Gamestate
  - Value 0: Game Start (All Tic-Tac-Toe Space Values should be 0)
  - Value 1: Player’s Turn Taken, ‘O’ placed
  - Value 2: Server’s Turn Taken, ‘X’ placed
  - Value 3: Game Over! “Cat’s game…”
  - Value 4: Game Over! “O wins!”
  - Value 5: Game Over! “X wins!”
- Int 3 - Int 11: Tic-Tac-Toe Space Values (Int 3 starts the top left space and subsequent Integers specify the spaces to the right, returning to the next row when reaching the end column)
  - Value 0: Blank
  - Value 1: ‘O’
  - Value 2: ‘X’
### Type 2:
- Int 1: Move Spot (This will be the integer that defines the spot on the board that the player wants to put their respective piece on, i.e. X or O. It will go from left-to-right, top-to-bottom—like how we read).
  - Value 1: Top-Left
  - Value 2: Top-Middle
  - Value 3: Top-Right
  - Value 4: Middle-Left
  - Value 5: Middle
  - Value 6: Middle-Right
  - Value 7: Bottom-Left
  - Value 8: Bottom-Middle
  - Value 9: Bottom-Right
### Type 3:
- Int 1: Player Piece/Turn (This will inform the client on which piece they will be using).
  - Value 0: “Spaces full. No more players may join.”
  - Value 1: ‘O’
  - Value 2: ‘X’
### Type 4:
- Int 1: Matchmaking (This will update the client about what is going happening on the other side of the game).
  - Value 0: Opponent is not connected.
  - Value 1: Opponent is connected
  - Value 2: Computer is now playing
### Type 5:
- Int 1: Invalid Input (This will update the client about what went wrong with their input).
  - Value 0: Input needs to be an integer
  - Value 1: Number selected is outside of range: 1-9
  - Value 2: Spot is taken
### Type 0 EXAMPLE:
1. If I'm the client and the game just started, then it’s the human player’s turn, and the human has to put an “O” down. The player puts the “O” in the middle space. The data sent to the server would be:
> [0, 13, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0]
> 
> [Type, Length, Count, Turn, Space_1, Space_2, …, Space_9]
2. I’m the server and just received this game data from the client:
> [0, 13, 5, 1, 2, 0, 1, 1, 1, 0, 2, 0, 0]
> 
> [Type, Length, Count, Turn, Space_1, Space_2, …, Space_9]
3. It’s the server’s turn now, and the server puts down a random “X” in an open space. This is the data it will send back:
> [0, 13, 6, 2, 2, 0, 1, 1, 1, 2, 2, 0, 0]
> 
> [Type, Length, Count, Turn, Space_1, Space_2, …, Space_9]
## Communication Failure Protocol:
- The Client and Server should abandon further attempts to play the game as soon as there is a communication failure.

