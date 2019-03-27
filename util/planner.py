from util.util import *
from util.castling import *
import requests
import time

HOST = "192.168.105.110"
GRIPPER_OPEN = 700
GRIPPER_CLOSED = 0
GRIPPER_DOWN = 100
GRIPPER_UP = 0
SLEEP_TIME_BETWEEN_REQUESTS = 0
IDLE_POSITION = {"x": 0, "y": 0}
DEAD_PIECE_POSITION = {"x": 100, "y": 100}

# the gripper's motion is limited to 0-100 but it is calibrated to be the middle of the squares,
# rather than the very edges of the board. These numbers essentially extend the board virtually,
# such that when the middle of the squares are being calculated they are correct. For example:
# the middle of square [0,0] will be roughly 0,0 and the middle of square [7,7] will roughly be
# 100,100.
BOARD_DIMENSIONS = {
    "left": -7,
    "top": -7,
    "right": 107,
    "bottom": 107
}

def plan(
    move, # a 4 length string move
    board="********/********/********/********/********/********/********/********",
            # the FEN notation with * for the state of the board
    enpassant="-" # the 2 length square string which is en passant
    ):
    print("Planning move: %s -> %s" % (move[0:2], move[2:4]))
    # print("Board dimensions:", boardDimensions)
    # print("Board:", board)

    assert len(move) == 4
    assert len(board) == 64 + 7
    assert len(enpassant) == 2 or enpassant == "-"

    splitBoard = board.split("/")
    assert len(splitBoard) == 8
    for row in splitBoard: assert len(row) == 8

    moveFrom = squareToCoordinates(move[0:2])
    moveTo   = squareToCoordinates(move[2:4])
    moveFromCoor = getSquareMiddle(moveFrom, BOARD_DIMENSIONS)
    moveToCoor   = getSquareMiddle(moveTo, BOARD_DIMENSIONS)

    # SPECIAL MOVES ############################################################

    # castling
    rookMove = castlingRookMove(move)
    piece = splitBoard[moveFrom["y"]][moveFrom["x"]]
    if (rookMove != None and (piece == "K" or piece == "k")):
        print("Castling!")
        movePiece(
            getSquareMiddle(rookMove["from"], BOARD_DIMENSIONS),
            getSquareMiddle(rookMove["to"], BOARD_DIMENSIONS)
        )

    # en passant
    if (move[2:4] == enpassant):
        print("En passant!")
        if (enpassant[1] == "3"): # 3 means it's on the top half, so the enpassant y pos will be 4
            pawnToTake = enpassant[0] + "4"
        else:                     # otherwise it's on the bottom half, so y pos is 5
            pawnToTake = enpassant[0] + "5"

        pawnSquare = squareToCoordinates(pawnToTake)
        pawnCoor = getSquareMiddle(pawnSquare, BOARD_DIMENSIONS)
        movePiece(moveFromCoor, moveToCoor)
        killPiece(pawnCoor)
        goIdle()
        return

    # NORMAL MOVES #############################################################

    # if the move to square is not empty, remove the piece from there first
    if (splitBoard[moveTo["y"]][moveTo["x"]] != "*"):
        print("Taking piece!")
        killPiece(moveToCoor)

    # move the piece normally
    movePiece(moveFromCoor, moveToCoor)
    goIdle()


    x = getch.getch() = ""):

    x = getch.getch()

    x = getch.getch()

    x = getch.getch()

    x = getch.getch()

    x = getch.getch()

    x = getch.getch()
    print(log)

    # response = requests.request(method, "http://{}:8000{}".format(HOST, endpoint), json=body)
    print((method, "http://{}:8000{}".format(HOST, endpoint), body))

    print("done.")
    time.sleep(SLEEP_TIME_BETWEEN_REQUESTS)
    # return response.text

def movePiece(moveFrom, moveTo):

    print("Moving a piece from", moveFrom, "to", moveTo)

    # Move to starting position at the top
    sendRequest("/position", body=moveFrom, setZ=GRIPPER_UP, log="moving to position...")

    # Open the gripper
    sendRequest("/gripper", body={"move": GRIPPER_OPEN}, log="opening gripper...")

    # Move down to the piece
    sendRequest("/position", body=moveFrom, setZ=GRIPPER_DOWN, log="moving down...")

    # Close the gripper
    sendRequest("/gripper", body={"move": GRIPPER_CLOSED}, log="closing gripper...")

    # Move gripper up with the piece
    sendRequest("/position", body=moveFrom, setZ=GRIPPER_UP, log="moving up...")

    # Move to destination position
    sendRequest("/position", body=moveTo, setZ=GRIPPER_UP, log="moving to destination...")

    # Move down to the board
    sendRequest("/position", body=moveTo, setZ=GRIPPER_DOWN, log="moving down...")

    # Release the piece onto the board
    sendRequest("/gripper", body={"move": GRIPPER_OPEN}, log="opening gripper...")

    # Move gripper back up
    sendRequest("/position", body=moveTo, setZ=GRIPPER_UP, log="moving up...")

    # Close the gripper
    sendRequest("/gripper", body={"move": GRIPPER_CLOSED}, log="closing gripper...")

# Go to idle position
def goIdle():
    print("Going idle.")
    sendRequest("/position", body=IDLE_POSITION, setZ=GRIPPER_UP, log="moving to idle position...")

def killPiece(moveFrom):

    print("Moving a piece from", moveFrom, "to the dead zone")
    
    # Move to starting position at the top
    sendRequest("/position", body=moveFrom, setZ=GRIPPER_UP, log="moving to position...")

    # Open the gripper
    sendRequest("/gripper", body={"move": GRIPPER_OPEN}, log="opening gripper...")

    # Move down to the piece
    sendRequest("/position", body=moveFrom, setZ=GRIPPER_DOWN, log="moving down...")

    # Close the gripper
    sendRequest("/gripper", body={"move": GRIPPER_CLOSED}, log="closing gripper...")

    # Move gripper up with the piece
    sendRequest("/position", body=moveFrom, setZ=GRIPPER_UP, log="moving up...")

    # Move to destination position
    sendRequest("/position", body=DEAD_PIECE_POSITION, setZ=GRIPPER_UP, log="moving to dead zone...")

    # TODO: need to wait for user to take the piece, then proceed
