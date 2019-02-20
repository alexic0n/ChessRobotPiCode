from util import squareToCoordinates

# both arguments are in FEN notation
def plan(move, board, coordinates, boardDimensions):
    assert len(move) == 4
    assert len(board) == 64 + 7

    board = board.split("/")
    moveFrom = squareToCoordinates(move[0:2])
    moveTo   = squareToCoordinates(move[2:4])
    moveFromCoor = coordinates[move[0:2]]
    moveToCoor   = coordinates[move[2:4]]

    # the middle of the square where the piece will move to
    moveToMiddleCoor = getSquareMiddle(moveTo, boardDimensions)

    actions = []

    # if the move to square is not empty, remove the piece from there first
    if (board[moveTo["y"]][moveTo["x"]] != "*"):
        actions.append(f"move to {moveToCoor['x']}, {moveToCoor['y']}")
        actions.append("pick up")
        actions.append("move off the board")
        actions.append("drop")

    # move the piece normally
    actions.append(f"move to {moveFromCoor['x']}, {moveFromCoor['y']}")
    actions.append("pick up")
    actions.append(f"move to {moveToMiddleCoor['x']}, {moveToMiddleCoor['y']}")
    actions.append("drop")
    actions.append("move off the board")

    return actions

# returns the middle of a square on a board
def getSquareMiddle(square, boardDimensions):
    squareSizeX = (boardDimensions["right"] - boardDimensions["left"]) / 8
    squareSizeY = (boardDimensions["bottom"] - boardDimensions["top"]) / 8

    return {
        "x": square["x"] * squareSizeX + squareSizeX / 2,
        "y": square["y"] * squareSizeY + squareSizeY / 2
    }
    

actions = plan(
    "a7a5",
    "bbbbbbbb/*bbbbbbb/********/********/b*******/********/wwwwwwww/wwwwwwww",
    {"a5": {"x": 25.6, "y": 57.6}, "a7": {"x": 46.2, "y": 64.2}},
    {"left": 3.6, "right": 102.4, "top": 4.5, "bottom": 121.3}
)

for action in actions:
    print(action)