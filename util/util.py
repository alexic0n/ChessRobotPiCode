import json

# maps a square string to [x, y] coordinates
def squareToCoordinates(square):

    if (len(square) != 2):
        raise ValueError("argument 'square' must be two characters long")

    # extract letter from square
    letter = square[:1]

    if (not letter.isupper() and not letter.islower()):
        raise ValueError("argument 'square' must start with a letter")

    # force lowercase
    if (letter.isupper()): letter = chr(ord(letter) + 32)

    # convert letter to number
    x = ord(letter) - 97

    if (x >= 8 or x < 0):
        raise ValueError("argument 'square' must start with a letter between 'a' and 'h'")
    
    # extract y from square
    y = int(square[1:2]) - 1

    if (y >= 8 or y < 0):
        raise ValueError("argument 'square' must end with a number between 1 and 8")

    return {"x": x, "y": y}
    
