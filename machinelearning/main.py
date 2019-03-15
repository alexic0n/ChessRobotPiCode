# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("../util/pythonchess")
import chess
import chess.engine
import cv2 as cv
import pyttsx3 as tts
import glob
sys.path.append("../")
from classes.aiInterface import *
from classes.segmentation import *
from util.util import *
import requests
import json

def userTurn(board, computerSide, topleft, bottomright, WorB, TextToSpeechEngine, vc): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        TextToSpeechEngine.say("Checkmate: Game Over!")
        TextToSpeechEngine.runAndWait()        
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
        TextToSpeechEngine.say("You are in check...save your king!")
        TextToSpeechEngine.runAndWait()

    continueGame = input("Type q to quit.")
    if(continueGame == "q"):
        return False

    TextToSpeechEngine.say("Make your move on the board.")
    TextToSpeechEngine.runAndWait()
    x = input("\nMake your move on the board.")

    # Capture image
    counter = 0
    while(counter < 5):
        ret,img = vc.read()
        counter += 1
    if img is None:
        return "imagereadfail"  
    cv.imwrite("images/image.jpg",img)    

    # Take last image from the webcam
    img_path = "images/image.jpg"
    image = cv.imread(img_path)

    image = image[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]

    cv.imwrite(img_path, image)
    userResponse = 'false'
    probability_rank = '0'
    currentLegalMoves = getLegalMoves(board)
    while (True):
        print('Making request to Tardis.')
        r = requests.post("http://www.checkmate.tardis.ed.ac.uk/pieces", files={
            'board': open(img_path, 'rb'),
            'fen': board.fen(),
            'validmoves': str(currentLegalMoves),
            'userResponse': userResponse,
            'probability_rank': probability_rank,
            'WorB': WorB
        })

        data = r.json()

        userResponse = data['userResponse']
        if userResponse == 'true':
            TextToSpeechEngine.say('Are you sure that you made a legal move?')
            TextToSpeechEngine.runAndWait()
            is_legal = input('Are you sure that you made a legal move? y or n\n')
            if is_legal == 'y':
                    probability_rank = str(int(data['probability_rank']) + 1)
            else:
                TextToSpeechEngine.say("Please make a new move.")
                TextToSpeechEngine.runAndWait()
                x = input("\nPlease make a new move.")

                # Capture image
                counter = 0
                while(counter < 5):
                    ret,img = vc.read()
                    counter += 1
                if img is None:
                    return "imagereadfail"
                cv.imwrite("images/image.jpg",img)

                # Take last image from the webcam
                img_path = "images/image.jpg"
                image = cv.imread(img_path)

                image = image[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]

                cv.imwrite(img_path, image)

                currentLegalMoves = getLegalMoves(board)
        else:
            data = r.json()
            TextToSpeechEngine.say(data['status'] + ". Is this correct?")
            TextToSpeechEngine.runAndWait()
            is_correct = input(data['status'] + ". Is this correct? y or n \n")
            if is_correct == 'y':
                move_str = data['move']
                move = chess.Move.from_uci(move_str)
                board.push(move)
                computerSide.userTurn(move)
                return True
            else:
                # NEXT PROBABLE MOVE
                status_list = data['status'].split(" ")
                piece = status_list[0]
                origin = status_list[3]
                TextToSpeechEngine.say("Have you moved a {} from {}?".format(piece, origin))
                TextToSpeechEngine.runAndWait()
                is_origin = input("Have you moved a {} from {}? y or n \n".format(piece, origin))
         
                if (is_origin == 'y'):
                    currentLegalMoves = [move for move in currentLegalMoves if not move == data['move']]
                else:
                    probability_rank = str(int(data['probability_rank']) + 1)

        if len(currentLegalMoves) == 0:
            TextToSpeechEngine.say("Your move is invalid. Please make a new move.")
            TextToSpeechEngine.runAndWait()
            x = input("\nYour move is invalid. Please make a new move.")

            # Capture image
            counter = 0
            while(counter < 5):
                ret,img = vc.read()
                counter += 1
            if img is None:
                return "imagereadfail"
            cv.imwrite("images/image.jpg",img)

            # Take last image from the webcam
            #paths = glob.glob('images/*.jpg')
            img_path = "images/image.jpg"
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
    vc = cv.VideoCapture(0)

    TextToSpeechEngine = tts.init()
    TextToSpeechEngine.setProperty("volume", 15)
    TextToSpeechEngine.setProperty("rate", 170)

    x = input("Please confirm the board is clear before proceeding.")
    TextToSpeechEngine.say("Please confirm the board is clear before proceeding.")
    TextToSpeechEngine.runAndWait()
    thinkTime = input("How long should I think per turn: ") #user can play as white or black, however for now it only works if white is at bottom of image and black is at top.
    TextToSpeechEngine.say("White or black?")
    TextToSpeechEngine.runAndWait()
    worB = input("W or b?\n")

    # Capture image
    counter = 0
    while(counter < 5):
        ret,img = vc.read()
        counter += 1
    if img is None:
        return "imagereadfail"
    cv.imwrite("images/image.jpg",img)

    # Take last image from the webcam
    #paths = glob.glob('images/*.jpg')
    img_path = "images/image.jpg"
    image = cv.imread(img_path)

    topleft, bottomright = segmentation_board(image) #find the coordinates of the board within the camera frame

    computerSide = ChessMatch(float(thinkTime)) #set up our AI interface, initialised with a time it may process the board for

    if(worB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make
            board.push(x)
            print("AI makes move: {}.".format(x),"\n")
            print(board)
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'b', TextToSpeechEngine, vc)
            print(board)
            if(not stopNow):
                computerSide.endgame()
                break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'w', TextToSpeechEngine, vc)
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
