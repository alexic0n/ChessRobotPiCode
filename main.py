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

    print("segmenting board...")
    ret,emptyboardimage = vc.read()
    # topleft, bottomright = segmentation_board(emptyboardimage)
    template, [topleft, bottomright] = segmentation_board(emptyboardimage)
    centerX = emptyboardimage.shape[0] / 2
    centerY = emptyboardimage.shape[1] / 2
    topleft = parallax_shift(topleft, [centerX, centerY], 100, 6)
    bottomright = parallax_shift(bottomright, [centerX, centerY], 100, 6)
    #if topleft[0] < 0: topleft[0] = 0
    #if topleft[1] < 0: topleft[1] = 0
    #if bottomright[0] > emptyboardimage.shape[0]: bottomright[0] = emptyboardimage.shape[0] - 1
    #if bottomright[1] > emptyboardimage.shape[1]: bottomright[1] = emptyboardimage.shape[0] - 1
    print("tl", topleft)
    print("xdiff", bottomright[0] - topleft[0])
    print("br", bottomright, "diff", topleft[0] - bottomright[0])
    print("ydiff", bottomright[1] - topleft[1])
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
