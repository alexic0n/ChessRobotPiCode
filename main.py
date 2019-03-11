# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("util/pythonchess")
import chess
import chess.engine
import cv2 as cv
import pyttsx3 as tts

from classes.aiInterface import *
from classes.redbluecoordinates import *
# from classes.segmentation import *
from util.segmentation_combine import *
from util.util import *
from util.parallax_shift import *
from util.planner import *

CAMERA_HEIGHT = 80
AVG_PIECE_HEIGHT = 6

def userTurn(board, computerSide, redblue, topleft, bottomright,vc,TextToSpeechEngine):
    #print("The current board state is:\n") #show the user the current board on command line
    #print(board)
    #print("\nYour legal moves are: ")
    #counter = 0
    #listOfLegalMoves = []
    #for a in board.legal_moves:
        #listOfLegalMoves.insert(counter,str(a))
        #print(a)
        #counter = counter + 1
    print("\nMake your move on the board.")
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
    realboard = redblue.getBoardState(topleft,bottomright,vc)
    if(realboard == "q"):
        return False
    if(realboard == "imagereadfail"):
        return userTurn(board,computerSide,redblue,topleft,bottomright,vc,TextToSpeechEngine)
    result, move = computerSide.userTurn(realboard)
    if not result:
        return userTurn(board,computerSide,redblue,topleft,bottomright,vc,TextToSpeechEngine)
    TextToSpeechEngine.say(str(move))
    print(str(move))
    TextToSpeechEngine.runAndWait()
    board.push(move)
    return True

# capture, segment, shift corners, check
def detectBoardLoop(vc):
    print("Segmenting board...")
    counter = 0
    while(counter < 5):
        ret,img = vc.read()
        counter += 1
    ret,emptyboardimage = vc.read()
    cv.imwrite("EMPTYBOARDIMAGE.jpg",emptyboardimage)

    # topleft, bottomright = segmentation_board(emptyboardimage)
    template, [topleft, bottomright] = segmentation_board(emptyboardimage, is_empty_board = True)

    cropped = emptyboardimage[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
    cv.imwrite("cropped.jpg",cropped)

    if (topleft == [0,0] and bottomright == [0,0]):
        inp = input("Could not find the board! Press Q to quit: ")
        if (inp == "q"): return None, None
        return detectBoardLoop(vc)

    boardShapeY = emptyboardimage.shape[0]
    boardShapeX = emptyboardimage.shape[1]
    centerX = boardShapeX / 2
    centerY = boardShapeY / 2

    print("Shifting...")
    topleft = parallax_shift(topleft, [centerX, centerY], CAMERA_HEIGHT, AVG_PIECE_HEIGHT)
    bottomright = parallax_shift(bottomright, [centerX, centerY], CAMERA_HEIGHT, AVG_PIECE_HEIGHT)

    if (topleft[0] < 0 or topleft[1] < 0 or bottomright[0] >= boardShapeX or bottomright[1] >= boardShapeY):
        inp = input("Could not see the whole board, center the board or move the camera upwards, press Q to quit: ")
        if (inp == "q"): return None, None
        return detectBoardLoop(vc)

    return topleft, bottomright

def gameplayloop(board):
    wOrB = input("White or black (w/b): ")
    thinkTime = input("How long should I think per turn: ")
    x = input("Please confirm the board is clear before proceeding.")
    vc = cv.VideoCapture(0)
    
    TextToSpeechEngine = tts.init()
    TextToSpeechEngine.setProperty("volume", 1)
    TextToSpeechEngine.setProperty("rate", 1)
    computerSide = ChessMatch(float(thinkTime))
    redblue = coordinateFinder()

    topleft, bottomright = detectBoardLoop(vc)

    if (topleft == None and bottomright == None):
        computerSide.endgame()
        exit()

    observedBoard = redblue.getBoardState(topleft,bottomright,vc, True)
    if observedBoard != "********/********/********/********/********/********/********/********":
        print("Board is not empty")
    
    while True:
        observedBoard = redblue.getBoardState(topleft,bottomright,vc, True)
        if observedBoard == "bbbbbbbb/bbbbbbbb/********/********/********/********/wwwwwwww/wwwwwwww": break
        input("Inital board state not found, please set up the board")

    
    if(wOrB == 'b'):
        while(True):
            x = computerSide.aiTurn()

            # Planning
            move = str(x)
            boardWithSpaces = computerSide.convertToFenWithSpaces(board.fen())
            coordinates = redblue.coordinates  # assume middle for all squares
            print
            boardDimensions = {
                "left": topleft[0], 
                "right": bottomright[0], 
                "top": topleft[1], 
                "bottom": bottomright[1]
            }
            if board.ep_square: enpassant = chess.square_name(board.ep_square)
            else: enpassant = "-"
            actions = plan(move, boardWithSpaces, coordinates, boardDimensions, enpassant)
            for action in actions: print("action:", action)

            board.push(x)
            print("AI makes move: {}.".format(x),"\n")
            print(board)
            stopNow = userTurn(board, computerSide, redblue, topleft, bottomright,vc,TextToSpeechEngine)
            if(not stopNow):
                computerSide.endgame()
                break
    else:
        while(True):
            stopNow = userTurn(board, computerSide, redblue, topleft, bottomright,vc,TextToSpeechEngine)
            if(not stopNow):
                computerSide.endgame()
                break
            x = computerSide.aiTurn()

            # Planning
            move = str(x)
            boardWithSpaces = computerSide.convertToFenWithSpaces(board.fen())
            coordinates = redblue.coordinates  # assume middle for all squares
            boardDimensions = {
                "left": topleft[0], 
                "right": bottomright[0], 
                "top": topleft[1], 
                "bottom": bottomright[1]
            }
            if board.ep_square: enpassant = chess.square_name(board.ep_square)
            else: enpassant = "-"
            actions = plan(move, boardWithSpaces, coordinates, boardDimensions, enpassant)
            for action in actions: print("action:", action)

            board.push(x)
            print("AI makes move: {}.".format(x),"\n")
            print(board)

def main():
    board = chess.Board()
    gameplayloop(board)

if __name__ == '__main__':
    main()
