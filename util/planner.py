# Use runPlanner.py to run this file !!!

from util.util import *
from util.castling import *
import requests
import time

HOST = "192.168.105.110"
GRIPPER_GRAB = -400
GRIPPER_RELEASE = GRIPPER_GRAB+500
GRIPPER_OPEN = 700
GRIPPER_CLOSED = 0

def _request(method, endpoint, body=None):
    response = requests.request(method, "http://{}:8000{}".format(HOST, endpoint), json=body)
    # print((method, "http://{}:8000{}".format(HOST, endpoint), body))
    return response.text


# move: a 4 length string move
# board: the FEN notation with * for the state of the board
# coordinates: a dictionary of squares and the coordinates of the pieces on them
# boardDimensions: a dictionary of coordinates for the sides of the board
# enpassant: the 2 length square string which is en passant
def plan(move, board, coordinates, boardDimensions, enpassant):
    print("Planning move: %s -> %s" % (move[0:2], move[2:4]))
    # print("Board dimensions:", boardDimensions)
    # print("Board:", board)

    # if no coordinates given, assume middle for all
    if coordinates == None:
        coordinates = allMiddleSquares(boardDimensions)

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
    for row in splitBoard: assert len(row) == 8

    moveFrom = squareToCoordinates(move[0:2])
    moveTo   = squareToCoordinates(move[2:4])
    moveFromCoor = coordinates[move[0:2]]
    moveToCoor   = coordinates[move[2:4]]

    # the middle of the square where the piece will move to
    # moveToMiddleCoor = getSquareMiddle(moveTo, boardDimensions)

    actions = []

    # SPECIAL MOVES ############################################################

    # castling
    rookMove = castlingRookMove(moveFrom, moveTo, splitBoard)
    if (rookMove != None):
        print("Castling!")
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
        print("En passant!")
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
        print("Taking piece!")
        actions += movePiece(moveToCoor, "off the board")

    # move the piece normally
    movePiece(moveFromCoor, moveToCoor)
    # actions.append("move to: off the board")

    # return actions

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
        "x": boardDimensions["left"] + square["x"] * squareSizeX + squareSizeX / 2,
        "y": boardDimensions["top"] + square["y"] * squareSizeY + squareSizeY / 2
    }

sleeptime = 0

def movePiece(moveFrom, moveTo):

    print("Moving from", moveFrom, "to", moveTo)
    
    # Move to starting position top
    moveFrom["z"] = 0
    print("moving to position...")
    _request("POST", "/position", body=moveFrom)
    print("done.")
    time.sleep(sleeptime)

    print("opening gripper...")
    _request("POST", "/gripper", body={"move":GRIPPER_OPEN})
    print("done.")
    time.sleep(sleeptime)

    # Move down
    print("moving down...")
    moveFrom["z"] = 100
    _request("POST", "/position", body=moveFrom)
    print("done.")
    time.sleep(sleeptime)

    # Squeeze the gripper    
    print("closing gripper...")
    _request("POST", "/gripper", body={"move":GRIPPER_CLOSED})
    print("done.")
    time.sleep(sleeptime)
    
    # Move up
    moveFrom["z"] = 0
    print("moving up...")
    _request("POST", "/position", body=moveFrom)
    print("done.")
    time.sleep(sleeptime)
    
    # Move to destination position top
    moveTo["z"] = 0
    print("moving to destination...")
    _request("POST", "/position", body=moveTo)
    print("done.")
    time.sleep(sleeptime)
    
    # Move down
    moveTo["z"] = 100
    print("moving down...")
    _request("POST", "/position", body=moveTo)
    print("done.")
    time.sleep(sleeptime)
    
    # Release
    print("opening gripper...")
    _request("POST", "/gripper", body={"move":GRIPPER_OPEN})
    print("done.")
    time.sleep(sleeptime)
    
    # Move back up
    moveTo["z"] = 0
    print("moving up...")
    _request("POST", "/position", body=moveTo)
    print("done.")
    time.sleep(sleeptime)

    print("closing gripper...")
    _request("POST", "/gripper", body={"move":GRIPPER_CLOSED})
    print("done.")
    time.sleep(sleeptime)
    print("finished with move.")

# returns a list of all squares and their middle positions
def allMiddleSquares(boardDimensions):
    out = {}
    squareSizeX = (boardDimensions["right"] - boardDimensions["left"]) / 8
    squareSizeY = (boardDimensions["bottom"] - boardDimensions["top"]) / 8 
    for x in range(8):
        for y in range(8):
            move = coordinatesToSquare({"x": x, "y": y})
            out[move] = {
                "y": boardDimensions["left"] + squareSizeX * x + squareSizeX / 2, 
                "x": boardDimensions["top"] + squareSizeY * y + squareSizeY / 2
            }
            print(x, y, move, out[move])
    return out

def planSimple(position):
    return plan(
        position,
        "********/********/********/********/********/********/********/********",
        None,
        {"left": -6.25, "right": 106.25, "top": 106.25, "bottom": -6.25},
        "-"
    )

