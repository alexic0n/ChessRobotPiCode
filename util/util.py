import json

# maps a square string to [x, y] coordinates
def squareToCoordinates(square, worB, fixed=False):

    assert len(square) == 2

    # extract letter from square
    letter = square[0]
    assert letter.isupper() or letter.islower()

    # force lowercase
    if (letter.isupper()): letter = chr(ord(letter) + 32)

    # convert letter to number
    y = ord(letter) - 97
    assert y >= 0 and y < 8
    
    # extract y from square
    x = int(square[1]) - 1
    assert x >= 0 and x < 8

    if (worB == 'w' or not fixed):
        return {"x": x, "y": y}
    else:
        return {"x": (7 - x), "y": (7 - y)}

# maps a [x, y] coordinate to a square string
def coordinatesToSquare(coordinates):
    x = coordinates["x"]
    y = coordinates["y"]
    assert x >= 0 and x < 8
    assert y >= 0 and y < 8

    return chr(x + 97) + str(7 - y + 1)

# returns the middle of a square on a board
def getSquareMiddle(square, boardDimensions):
    squareSizeX = (boardDimensions["right"] - boardDimensions["left"]) / 8
    squareSizeY = (boardDimensions["bottom"] - boardDimensions["top"]) / 8

    # squareSizeX = 100 / 8
    # squareSizeY = 100 / 8

    # return {
    #     "x": boardDimensions["left"] + square["x"] * squareSizeX + squareSizeX / 2,
    #     "y": boardDimensions["top"] + square["y"] * squareSizeY + squareSizeY / 2
    # }

    # print(boardDimensions, square["x"] * squareSizeX)

    return {
        "x":boardDimensions["left"] + square["x"] * squareSizeX + squareSizeX / 2,
        "y":boardDimensions["top"] + square["y"] * squareSizeY + squareSizeY / 2 
    }

