# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("util/pythonchess")
import chess
import chess.engine
import cv2 as cv
from classes.aiInterface import *
from classes.redbluecoordinates import *
# from classes.segmentation import *
from util.segmentation_combine import *
from util.util import *
from util.parallax_shift import *
from util.planner import *

def userTurn(board, computerSide, redblue, topleft, bottomright,vc):
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
        return userTurn(board,computerSide,redblue,topleft,bottomright,vc)
    result, move = computerSide.userTurn(realboard)
    if not result:
        return userTurn(board,computerSide,redblue,topleft,bottomright,vc)
    board.push(move)
    return True

def gameplayloop(board):
    wOrB = input("White or black (w/b): ")
    thinkTime = input("How long should I think per turn: ")
    x = input("Please confirm the board is clear before proceeding.")
    vc = cv.VideoCapture(0)
    ret,emptyboardimage = vc.read()
    template, [topleft, bottomright] = segmentation_board(emptyboardimage)
    centerX = emptyboardimage.shape[0] / 2
    centerY = emptyboardimage.shape[1] / 2
    topleft = parallax_shift(topleft, [centerX, centerY], 100, 6)
    bottomright = parallax_shift(bottomright, [centerX, centerY], 100, 6)
    print("tl", topleft)
    print("br", bottomright)
    computerSide = ChessMatch(float(thinkTime))
    redblue = coordinateFinder()
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
            stopNow = userTurn(board, computerSide, redblue, topleft, bottomright,vc)
            if(not stopNow):
                computerSide.endgame()
                break
    else:
        while(True):
            stopNow = userTurn(board, computerSide, redblue, topleft, bottomright,vc)
            print(redblue.coordinates)
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
