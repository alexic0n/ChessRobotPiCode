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
from classes.segmentation import *
from util.util import *

def userTurn(board, computerSide, redblue, topleft, bottomright,vc): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    print("\nMake your move on the board.") #if it returns false, the game ends, otherwise the game continues through another recursive loop
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
    wOrB = input("White or black (w/b): ") #determine the user settings for the game, if you want to win I recommend 0.0001 deconds think time
    thinkTime = input("How long should I think per turn: ") #user can play as white or black, however for now it only works if white is at bottom of image and black is at top.
    x = input("Please confirm the board is clear before proceeding.")
    vc = cv.VideoCapture(0)
    ret,emptyboardimage = vc.read()
    topleft, bottomright = segmentation_board(emptyboardimage) #find the coordinates of the board within the camera frame
    topleft[0] -= 20 #factor in parallax, will be tuned when final hardware design is established
    topleft[1] -=20
    bottomright[0] += 20
    bottomright[1] +=20
    computerSide = ChessMatch(float(thinkTime)) #set up our AI interface, initialised with a time it may process the board for
    redblue = coordinateFinder()
    if(wOrB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make
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
            if(not stopNow):
                computerSide.endgame()
                break
            x = computerSide.aiTurn()
            board.push(x)
            print("AI makes move: {}.".format(x),"\n")
            print(board)

def main():
    board = chess.Board()
    gameplayloop(board)

if __name__ == '__main__':
    main()
