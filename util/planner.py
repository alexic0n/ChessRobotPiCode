from util import *

# both arguments are in FEN notation
def plan(move, board, coordinates, boardDimensions, enpassant):
    assert len(move) == 4
    assert len(board) == 64 + 7
    assert boardDimensions["left"] != None
    assert boardDimensions["right"] != None
    assert boardDimensions["top"] != None
    assert boardDimensions["bottom"] != None
    assert len(enpassant) == 2 or enpassant == "-"

    for square in coordinates:
        assert len(square) == 2
        assert coordinates[square]["x"] != None
        assert coordinates[square]["y"] != None

    splitBoard = board.split("/")
    assert len(splitBoard) == 8

    moveFrom = squareToCoordinates(move[0:2])
    moveTo   = squareToCoordinates(move[2:4])
    moveFromCoor = coordinates[move[0:2]]
    moveToCoor   = coordinates[move[2:4]] if move[2:4] in coordinates.keys() else None

    # the middle of the square where the piece will move to
    moveToMiddleCoor = getSquareMiddle(moveTo, boardDimensions)

    actions = []

    # SPECIAL MOVES ############################################################

    # castling
    rookMove = castlingRookMove(moveFrom, moveTo, splitBoard)
    if (rookMove != None):
        print("CASTLING!")
        rookSquare = coordinatesToSquare(rookMove["from"])
        actions += movePiece(moveFromCoor, moveToMiddleCoor)
        actions += movePiece(
            coordinates[rookSquare],
            getSquareMiddle(rookMove["to"], boardDimensions)
        )
        actions.append("move to: off the board")

        return actions

    # en passant
    if (move[2:4] == enpassant):
        print("EN PASSANT!")
        if (enpassant[1] == "3"):
            pawnToTake = enpassant[0] + "4"
        else:
            pawnToTake = enpassant[0] + "5"

        pawnCoor = coordinates[pawnToTake]
        actions += movePiece(moveFromCoor, moveToMiddleCoor)
        actions += movePiece(pawnCoor, "off the board")
        return actions

    # NORMAL MOVES #############################################################

    # if the move to square is not empty, remove the piece from there first
    if (splitBoard[moveTo["y"]][moveTo["x"]] != "*"):
        print("TAKING PIECE!")
        actions += movePiece(moveToCoor, "off the board")

    # move the piece normally
    actions += movePiece(moveFromCoor, moveToMiddleCoor)
    actions.append("move to: off the board")

    return actions

# returns the middle of a square on a board
def getSquareMiddle(square, boardDimensions):
    squareSizeX = (boardDimensions["right"] - boardDimensions["left"]) / 8
    squareSizeY = (boardDimensions["bottom"] - boardDimensions["top"]) / 8

    return {
        "x": square["x"] * squareSizeX + squareSizeX / 2,
        "y": square["y"] * squareSizeY + squareSizeY / 2
    }

def movePiece(moveFrom, moveTo):
    return [
        f"move to: {moveFrom}",
        "pick up",
        f"move to: {moveTo}",
        "drop"
    ]

def castlingRookMove(moveFrom, moveTo, splitBoard):
    y = moveFrom["y"]
    isWhiteKing = splitBoard[y][moveFrom["x"]] == "K"
    isBlackKing = splitBoard[y][moveFrom["x"]] == "k"
    movedLeftTwo = moveFrom["x"] - moveTo["x"] == 2
    movedRightTwo = moveFrom["x"] - moveTo["x"] == -2
    leftIsWhiteRook = splitBoard[y][0] == "R"
    rightIsWhiteRook = splitBoard[y][7] == "R"
    leftIsBlackRook = splitBoard[y][0] == "r"
    rightIsBlackRook = splitBoard[y][7] == "r"

    if (isWhiteKing and movedLeftTwo and leftIsWhiteRook):
        return {"from": {"x": 0, "y": y}, "to": {"x": 3, "y": y}}
    if (isWhiteKing and movedRightTwo and rightIsWhiteRook):
        return {"from": {"x": 7, "y": y}, "to": {"x": 5, "y": y}}
    if (isBlackKing and movedLeftTwo and leftIsBlackRook):
        return {"from": {"x": 0, "y": y}, "to": {"x": 3, "y": y}}
    if (isBlackKing and movedRightTwo and rightIsBlackRook):
        return {"from": {"x": 7, "y": y}, "to": {"x": 5, "y": y}}

    return None




# EXAMPLE USES #################################################################

print("\nNORMAL MOVE")
actions = plan(
    "a2a4",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR",
    {"a2": {"x": 0.51, "y": 6.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)

for action in actions:
    print(action)


print("\nTAKE PIECE")
actions = plan(
    "b3a4",
    "rnbqkbnr/*ppppppp/********/********/p*******/*P******/P*PPPPPP/RNBQKBNR",
    {"b3": {"x": 1.51, "y": 5.51}, "a4": {"x": 0.51, "y": 4.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)

for action in actions:
    print(action)


print("\nEN PASSANT")
actions = plan(
    "b4a3",
    "rnbqkbnr/p*pppppp/********/********/Pp******/********/*PPPPPPP/RNBQKBNR",
    {"a4": {"x": 0.51, "y": 4.51}, "b4": {"x": 1.51, "y": 4.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "a3"
)

for action in actions:
    print(action)


print("\nEN PASSANT THE OTHER WAY")
actions = plan(
    "a5b6",
    "rnbqkbnr/p*pppppp/********/Pp******/********/********/*PPPPPPP/RNBQKBNR",
    {"a5": {"x": 0.51, "y": 3.51}, "b5": {"x": 1.51, "y": 3.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "b6"
)

for action in actions:
    print(action)


print("\nCASTLING RIGHT TOP")
actions = plan(
    "e8g8",
    "rnbqk**r/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR",
    {"e8": {"x": 4.51, "y": 0.51}, "h8": {"x": 7.51, "y": 0.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)

for action in actions:
    print(action)


print("\nCASTLING LEFT TOP")
actions = plan(
    "e8c8",
    "r***kbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR",
    {"e8": {"x": 4.51, "y": 0.51}, "a8": {"x": 0.51, "y": 0.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)

for action in actions:
    print(action)


print("\nCASTLING RIGHT BOTTOM")
actions = plan(
    "e1g1",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQK**R",
    {"e1": {"x": 4.51, "y": 7.51}, "h1": {"x": 7.51, "y": 7.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)

for action in actions:
    print(action)


print("\nCASTLING LEFT BOTTOM")
actions = plan(
    "e1c1",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/R***KBNR",
    {"e1": {"x": 4.51, "y": 7.51}, "a1": {"x": 0.51, "y": 7.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)

for action in actions:
    print(action)