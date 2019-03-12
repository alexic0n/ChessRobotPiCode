# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("../util/pythonchess")
import chess
import chess.engine
import cv2 as cv
import glob
sys.path.append("../")
from classes.aiInterface import *
from classes.segmentation import *
from util.util import *
import requests
import json

def userTurn(board, computerSide, topleft, bottomright, WorB): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
    continueGame = input("Type q to quit.")
    if(continueGame == "q"):
        return False

    # print("\nMake your move on the board.") #if it returns false, the game ends, otherwise the game continues through another recursive loop
    x = input("\nMake your move on the board.")
    # Take last image from the webcam
    paths = glob.glob('images/*.jpg')
    img_path = paths[len(paths) - 1]
    print(img_path)
    image = cv.imread(img_path)

    image = image[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]

    cv.imwrite(img_path, image)
    userResponse = 'false'
    probability_rank = '0'
    currentLegalMoves = getLegalMoves(board)
    while (True):
        print(currentLegalMoves)
        print('Making request to Tardis.')
        r = requests.post("http://www.checkmate.tardis.ed.ac.uk/pieces", files={
            'board': open(img_path, 'rb'),
            'fen': board.fen(),
            'validmoves': str(currentLegalMoves),
            'userResponse': userResponse,
            'probability_rank': probability_rank,
            'WorB': WorB
        })

        print(r)

        data = r.json()

        userResponse = data['userResponse']
        if userResponse == 'true':
            is_legal = input('Are you sure that you made a legal move? y or n\n')
            if is_legal == 'y':
                    probability_rank = str(int(data['probability_rank']) + 1)

            else:
                x = input("\nPlease make a new move.")
                # Take last image from the webcam
                paths = glob.glob('images/*.jpg')
                img_path = paths[len(paths) - 1]
                print(img_path)
                image = cv.imread(img_path)

                image = image[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]

                cv.imwrite(img_path, image)

                currentLegalMoves = getLegalMoves(board)
        else:
            data = r.json()
            is_correct = input(data['status'] + " Is this correct? y or n \n")
            if is_correct == 'y':
                move_str = data['move']
                move = chess.Move.from_uci(move_str)
                board.push(move)
                computerSide.userTurn(move)
                return True
            else:
                # NEXT PROBABLE MOVE
                currentLegalMoves = [move for move in currentLegalMoves if not move == data['move']]

        if len(currentLegalMoves) == 0:
            x = input("\nYour move is invalid. Please make a new move.")
            # Take last image from the webcam
            paths = glob.glob('images/*.jpg')
            img_path = paths[len(paths) - 1]
            print(img_path)
            image = cv.imread(img_path)

            image = image[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]

            cv.imwrite(img_path, image)

            currentLegalMoves = getLegalMoves(board)

def getLegalMoves(board):
    x = board.legal_moves
    legalMoves = []
    for move in x:
        legalMoves.append(str(move))
    return legalMoves

def gameplayloop(board):
    thinkTime = input("How long should I think per turn: ") #user can play as white or black, however for now it only works if white is at bottom of image and black is at top.
    x = input("Please confirm the board is clear before proceeding.")
    worB = input("W or b?\n")

    # Take last image from the webcam
    paths = glob.glob('images/*.jpg')
    img_path = paths[len(paths) - 1]
    image = cv.imread(img_path)

    topleft, bottomright = segmentation_board(image) #find the coordinates of the board within the camera frame

    computerSide = ChessMatch(float(thinkTime)) #set up our AI interface, initialised with a time it may process the board for

    if(worB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make
            board.push(x)
            print("AI makes move: {}.".format(x),"\n")
            print(board)
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'b')
            print(board)
            if(not stopNow):
                computerSide.endgame()
                break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'w')
            print(board)
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
