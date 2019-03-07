# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("util/pythonchess")
import chess
import chess.engine
import cv2 as cv
import glob
from classes.aiInterface import *
from classes.segmentation import *
from util.util import *
import requests
import json

def userTurn(board, computerSide, topleft, bottomright): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    print("\nMake your move on the board.") #if it returns false, the game ends, otherwise the game continues through another recursive loop
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
    continueGame = input("Type q to quit.")
    if(continueGame == "q"):
        return False

    # Take last image from the webcam
    paths = glob.glob('Logitech Webcam/*.jpg')
    img_path = paths[len(paths) - 1]
    image = cv.imread(img_path)

    image = image[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]

    cv.imwrite(img_path, image)
    currentLegalMoves = getLegalMoves(board)

    r = requests.post("http://www.checkmate.tardis.ed.ac.uk/learn", files={
        'img': open(img_path, 'rb'),
        'fen': board.fen(),
        'moves': currentLegalMoves
    })

    data = r.json()

    realboard = data['fen']

    #realboard = redblue.getBoardState(topleft,bottomright)
    # Server will send the fen notation and store it in realboard
    if(realboard == "q"):
        return False
    if(realboard == "imagereadfail"):
        return userTurn(board,computerSide,topleft,bottomright)
    result, move = computerSide.userTurn(realboard)
    if not result:
        return userTurn(board,computerSide,topleft,bottomright)
    board.push(move)
    return True

def getLegalMoves(board):
    x = board.legal_moves()
    legalMoves = []
    for move in x:
        legalMoves.append(str(move))
    return json.dumps(legalMoves)

def gameplayloop(board):
    thinkTime = input("How long should I think per turn: ") #user can play as white or black, however for now it only works if white is at bottom of image and black is at top.
    x = input("Please confirm the board is clear before proceeding.")

    # Take last image from the webcam
    paths = glob.glob('Logitech Webcam/*.jpg')
    img_path = paths[len(paths) - 1]
    image = cv.imread(img_path)

    topleft, bottomright = segmentation_board(image) #find the coordinates of the board within the camera frame

    computerSide = ChessMatch(float(thinkTime)) #set up our AI interface, initialised with a time it may process the board for

    # if(wOrB == 'b'): #run the game recursively until the user quits or checkmate is achieved
    #     while(True):
    #         x = computerSide.aiTurn() #obtain the move the ai would make
    #         board.push(x)
    #         print("AI makes move: {}.".format(x),"\n")
    #         print(board)
    #         stopNow = userTurn(board, computerSide, topleft, bottomright)
    #         if(not stopNow):
    #             computerSide.endgame()
    #             break
    # else:
    while (True):
        stopNow = userTurn(board, computerSide, topleft, bottomright)
        if (not stopNow):
            computerSide.endgame()
            break
        x = computerSide.aiTurn()
        board.push(x)
        print("AI makes move: {}.".format(x), "\n")
        print(board)

def main():
    board = chess.Board()
    gameplayloop(board)

if __name__ == '__main__':
    main()
