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

def userTurn(board, computerSide):
    print("The current board state is:\n")
    print(board)
    print("\nYour legal moves are: ")
    counter = 0
    listOfLegalMoves = []
    for a in board.legal_moves:
        listOfLegalMoves.insert(counter,str(a))
        print(a)
        counter = counter + 1
    moveChoice = input("Please input your choice, or type q if you want to end the game: ")
    if moveChoice == 'q':
        return False
    if moveChoice in listOfLegalMoves:
        myMove = chess.Move.from_uci(moveChoice)
        board.push(myMove)
        x = computerSide.convertBW(board.fen().split(' ')[0])
        computerSide.userTurn(x)
        return True
    else:
        print("That move is illegal! Try again.")
        return userTurn(board)

def gameplayloop(board):
    wOrB = input("White or black (w/b): ")
    thinkTime = input("How long should I think per turn: ")
    computerSide = ChessMatch(float(thinkTime))
    if(wOrB == 'b'):
        while(True):
            x = computerSide.aiTurn()
            board.push(x)
            stopNow = userTurn(board, computerSide)
            if(not stopNow):
                computerSide.endgame()
                break
    else:
        while(True):
            stopNow = userTurn(board, computerSide)
            if(not stopNow):
                computerSide.endgame()
                break
            x = computerSide.aiTurn()
            board.push(x)

def main():
    board = chess.Board()
    gameplayloop(board)

if __name__ == '__main__':
    main()
