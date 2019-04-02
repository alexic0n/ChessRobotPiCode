import sys
from util.util import *
import requests
import time
import wave
import getch
sys.path.append("../")
from dictionary import print_play, play_sound

HOST = "ev3"
GRIPPER_OPEN = 650
GRIPPER_CLOSED = 0
GRIPPER_DOWN = 100
GRIPPER_UP = 0
SLEEP_TIME_BETWEEN_REQUESTS = 0
IDLE_POSITION = {"x": 100, "y": 50}
DEAD_PIECE_POSITION = {"x": 0, "y": 50}

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

def text_to_speech(text, lang):
    r = requests.post("http://www.checkmate.tardis.ed.ac.uk/text_to_speech", files={
            'text': text,
            'lang': lang
        })

    with wave.open('sounds/audio.wav','wb') as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(26500)
            file.writeframes(r.content)
    
    play_sound('sounds/audio.wav')
    
def waitForConfirmationInput():
    confirmed = getch.getch()
    if(confirmed == '1'):
        return True
    elif(confirmed =='q'):
        sys.exit()
    else:
        return waitForConfirmationInput()

def plan(
    move, # a 4 length string move
    lang,
    worB,
    board="********/********/********/********/********/********/********/********",
            # the FEN notation with * for the state of the board
    enpassant="-",
    replay=False):  # the 2 length square string which is en passant
    
    print("Planning move: %s -> %s" % (move[0:2], move[2:4]))
    # print("Board dimensions:", boardDimensions)
    # print("Board:", board)

    assert len(move) == 4 or len(move) == 5
    assert len(board) == 64 + 7
    assert len(enpassant) == 2 or enpassant == "-"

    splitBoard = board.split("/")
    assert len(splitBoard) == 8
    for row in splitBoard: assert len(row) == 8
    
    splitBoard = splitBoard[::-1]
    print(splitBoard)

    moveFromChessCoord = squareToCoordinates(move[0:2], worB, False)
    moveToChessCoord = squareToCoordinates(move[2:4], worB, False)

    moveFrom = squareToCoordinates(move[0:2], worB, True)
    moveTo   = squareToCoordinates(move[2:4], worB, True)
    moveFromCoor = getSquareMiddle(moveFrom, BOARD_DIMENSIONS)
    moveToCoor   = getSquareMiddle(moveTo, BOARD_DIMENSIONS)

    # SPECIAL MOVES ############################################################

    # castling
    rookMove, kingMove = castlingRookMove(move)
    piece = splitBoard[moveFromChessCoord["x"]][moveFromChessCoord["y"]]
    print(piece, rookMove, kingMove)
    if (rookMove != None and (piece == "K" or piece == "k")):
        print("Castling!")
        movePiece(
            getSquareMiddle(squareToCoordinates(rookMove[0:2], worB, True), BOARD_DIMENSIONS),
            getSquareMiddle(squareToCoordinates(rookMove[2:4], worB, True), BOARD_DIMENSIONS)
        )
        movePiece(
            getSquareMiddle(squareToCoordinates(kingMove[0:2], worB, True), BOARD_DIMENSIONS),
            getSquareMiddle(squareToCoordinates(kingMove[2:4], worB, True), BOARD_DIMENSIONS)
        )
        if (not replay):
            goIdle()
        return

    # en passant
    if (move[2:4] == enpassant):
        print("En passant!")
        if (enpassant[1] == "3"): # 3 means it's on the top half, so the enpassant y pos will be 4
            pawnToTake = enpassant[0] + "4"
        else:                     # otherwise it's on the bottom half, so y pos is 5
            pawnToTake = enpassant[0] + "5"

        pawnSquare = squareToCoordinates(pawnToTake, worB, True)
        pawnCoor = getSquareMiddle(pawnSquare, BOARD_DIMENSIONS)
        movePiece(moveFromCoor, moveToCoor)
        killPiece(pawnCoor, lang)
        if (not replay):
            goIdle()
        return

    # NORMAL MOVES #############################################################

    # if the move to square is not empty, remove the piece from there first
    if (splitBoard[moveToChessCoord["x"]][moveToChessCoord["y"]] != "*"):
        print("Taking piece!")
        killPiece(moveToCoor, lang)

    # move the piece normally
    movePiece(moveFromCoor, moveToCoor)
    if (not replay):
        goIdle()

# given the move for the king, return the move that the rook needs to make
def castlingRookMove(move):
    print(move)
    if (move == "e8g8" or move == "e8h8"): return "h8f8", "e8g8"
    if (move == "e8c8" or move == "e8a8"): return "a8d8", "e8c8"
    if (move == "e1g1" or move == "e1h1"): return "h1f1", "e1g1"
    if (move == "e1c1" or move == "e1a1"): return "a1d1", "e1c1"
    return None, move

def sendRequest(endpoint, body = None, setZ = None, log = ""):
    method = "POST"
    
    # for z: 0 is at the top, 100 is at the bottom
    if (setZ != None):
        body["z"] = setZ

    print(log)

    response = requests.request(method, "http://{}:8000{}".format(HOST, endpoint), json=body)
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

def killPiece(moveFrom, lang):

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
    
    if (lang == 'en'):    
        text_to_speech("Piece taken! Please remove it from the gripper and press yes.", lang)
    if (lang == 'es'):
        text_to_speech("Pieza tomada Por favor, sáquelo de la pinza y presione sí.", lang)
    if (lang == 'fr'):    
        text_to_speech("Pièce prise! Veuillez le retirer de la pince et appuyer sur Oui.", lang)
    if (lang == 'de'):
        text_to_speech("Figur geschlagen! Bitte nehmen Sie die Figur aus dem Greifer und drücken Sie Ja.", lang)
    if (lang == 'zh-cn'):    
        text_to_speech("吃子！请将棋子从夹子上取下并按确认键。", lang)

    waitForConfirmationInput()

    # TODO: need to wait for user to take the piece, then proceed
