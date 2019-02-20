import json

# maps a square string to [x, y] coordinates
def squareToCoordinates(square):

    assert len(square) == 2

    # extract letter from square
    letter = square[0]
    assert letter.isupper() or letter.islower()

    # force lowercase
    if (letter.isupper()): letter = chr(ord(letter) + 32)

    # convert letter to number
    x = ord(letter) - 97
    assert x >= 0 and x < 8
    
    # extract y from square
    y = int(square[1]) - 1
    assert y >= 0 and y < 8

    return {"x": x, "y": y}
