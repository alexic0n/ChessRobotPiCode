# given the move for the king, return the move that the rook needs to make
def castlingRookMove(moveFrom, moveTo, board):
    row = moveFrom["y"]
    distanceMoved = moveTo["x"] - moveFrom["x"] # positive is right
    king = board[moveFrom["y"]][moveFrom["x"]]

    if king == "K": rook = "R"
    elif king == "k": rook = "r"
    else: return None

    if (distanceMoved == 2): direction = 1      # right
    if (distanceMoved == -2): direction = -1    # left
    if (abs(distanceMoved) != 2): return None

    # returns the location of the rook in the direction specified from the king
    rookLoc = findRook(moveFrom, direction, board, rook)

    nextToKing = {"x": moveFrom["x"] + direction, "y": moveFrom["y"]}
    return {"from": rookLoc, "to": nextToKing}


def findRook(king, direction, board, rookToFind):
    square = king

    # move in the direction
    while (square["x"] < 8 and square["x"] >= 0):
        if (board[square["y"]][square["x"]] == rookToFind): return square
        square = {"x": square["x"] + direction, "y": square["y"]}

    return None
