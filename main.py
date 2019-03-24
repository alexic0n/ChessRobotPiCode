# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("./util/pythonchess")
import chess
import chess.engine
import cv2 as cv
import pyttsx3 as tts
import glob
import getch

sys.path.append("./")
from classes.aiInterface import *
from classes.segmentation_analysis import *
from util.util import *
from util.planner import *
import requests
import json
from crop import crop_squares

img_path = "images/image.jpg"

def userTurn(board, computerSide, topleft, bottomright, WorB, TextToSpeechEngine, vc, firstImage, rotateImage): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        TextToSpeechEngine.say("Checkmate: Game Over!")
        TextToSpeechEngine.runAndWait()
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
        TextToSpeechEngine.say("You are in check...save your king!")
        TextToSpeechEngine.runAndWait()

    print("Type q to quit.")
    if(getch.getch() == "q"):
        return False

    TextToSpeechEngine.say("Make your move on the board. Confirm by pressing 1.")
    TextToSpeechEngine.runAndWait()
    print("Make your move on the board. Confirm by pressing 1.")
    waitForConfirmationInput()

    # Capture image
    counter = 0
    while(counter < 5):
        ret,img = vc.read()
        counter += 1
    img = img[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
    cv.imwrite(img_path, img)

    probability_rank = '0'
    currentLegalMoves = getLegalMoves(board)
    originKnown = False
    kingside = 'false'
    queenside = 'false'

    # Check if castling move is available
    fen = board.fen()
    castling = fen.split(" ")[2]
    if (WorB == 'w'):
        castling_moves = []
        lastRow = fen.split(" ")[0].split("/")[7]
        if "K" in castling:
            if lastRow[-2] == "2":
                kingside = 'true'
                castling_moves.append("f1")
        if "Q" in castling:
            if lastRow[1] == "3":
                queenside = 'true'
                castling_moves.append("c1")
        if queenside or kingside:
            castling_moves.append("e1")

    else:
        castling_moves = []
        firstRow = fen.split(" ")[0].split("/")[0]
        if "k" in castling:
            if firstRow[-2] == "2":
                kingside = 'true'
                castling_moves.append("f8")
        if "q" in castling:
            if firstRow[1] == "3":
                queenside = 'true'
                castling_moves.append("c8")
        if queenside or kingside:
            castling_moves.append("e8")


    incorrect_count = 0

    while (True):
        print('Making request to Tardis.')
        r = requests.post("http://www.checkmate.tardis.ed.ac.uk/pieces", files={
            'board': open(img_path, 'rb'),
            'fen': board.fen(),
            'validmoves': str(currentLegalMoves),
            'kingside': kingside,
            'queenside': queenside,
            'probability_rank': probability_rank,
            'WorB': WorB,
            'firstImage': firstImage,
            'rotateImage': rotateImage
        })

        firstImage = 'false'

        data = r.json()

        rotateImage = data['rotateImage']

        if (len(data['move']) == 5):
            if (data['move'][2] == "a"):
                # Queenside castling
                TextToSpeechEngine.say("You have made queenside castling. Is this correct?")
                TextToSpeechEngine.runAndWait()
                print("You have made queenside castling. Is this correct? y or n")
                is_correct = waitForConfirmationInputYesNo()
                if (is_correct == 'n'):
                    queenside = 'false'

            if (data['move'][2] == "h"):
                # Kingside castling
                TextToSpeechEngine.say("You have made kingside castling. Is this correct?")
                TextToSpeechEngine.runAndWait()
                print("You have made kingside castling. Is this correct? y or n")
                is_correct = waitForConfirmationInputYesNo()
                if (is_correct == 'n'):
                    kingside = 'false'

        else:
            TextToSpeechEngine.say(data['status'] + ". Is this correct?")
            TextToSpeechEngine.runAndWait()
            print(data['status'] + ". Is this correct? y or n")
            is_correct = waitForConfirmationInputYesNo()

        if is_correct == 'y':
            if (len(data['move']) == 5):
                move_str = data['move'][0:4]
            else:
                move_str = data['move']

            print(move_str)
            move = chess.Move.from_uci(move_str)
            board.push(move)
            computerSide.userTurn(move)
            return True

        else:
            # NEXT PROBABLE MOVE
            if not originKnown:
                status_list = data['status'].split(" ")
                piece = status_list[0]
                origin = status_list[3]
                if not (len(data['move']) == 5):
                    TextToSpeechEngine.say("Have you moved a {} from {}?".format(piece, origin))
                    TextToSpeechEngine.runAndWait()
                    print("Have you moved a {} from {}? y or n".format(piece, origin))
                    is_origin = waitForConfirmationInputYesNo()
                    if (is_origin == 'y'):
                        originKnown = True
                        currentLegalMoves = [move for move in currentLegalMoves if not move == data['move'] and move[0:2] == origin]
                    else:
                        incorrect_count = incorrect_count + 1
                        if incorrect_count == 2:
                            TextToSpeechEngine.say('Are you sure that you made a legal move?')
                            TextToSpeechEngine.runAndWait()
                            print('Are you sure that you made a legal move? y or n')
                            is_legal = waitForConfirmationInputYesNo()

                            if is_legal == 'y':
                                probability_rank = str(int(data['probability_rank']) + 1)
                            else:
                                TextToSpeechEngine.say("Please make a new move. Press 1 to confirm.")
                                TextToSpeechEngine.runAndWait()
                                print("Please make a new move. Press 1 to confirm.")
                                waitForConfirmationInput()
                                originKnown = False
                                incorrect_count = 0

                                # Capture image
                                counter = 0
                                while(counter < 5):
                                    ret,img = vc.read()
                                    counter += 1
                                img = img[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
                                cv.imwrite(img_path, img)

                                currentLegalMoves = getLegalMoves(board)
                        else:
                            probability_rank = str(int(data['probability_rank']) + 1)
                            currentLegalMoves = [move for move in currentLegalMoves if not move[0:2] == origin]
            else:
                currentLegalMoves = [move for move in currentLegalMoves if not move == data['move']]

        if (len(currentLegalMoves) == 0):
            TextToSpeechEngine.say("Your move is invalid. Please make a new move. Confirm new move by pressing 1.")
            TextToSpeechEngine.runAndWait()
            print("Your move is invalid. Please make a new move and confirm when you have done so by pressing 1.")
            waitForConfirmationInput()
            incorrect_count = 0
            originKnown = False

            # Capture image
            counter = 0
            while(counter < 5):
                ret,img = vc.read()
                counter += 1
            img = img[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
            cv.imwrite(img_path, img)

            currentLegalMoves = getLegalMoves(board)

def getLegalMoves(board):
    x = board.legal_moves
    legalMoves = []
    for move in x:
        legalMoves.append(str(move))
    return legalMoves

def waitForConfirmationInputYesNo():
    return getch.getch()

def waitForConfirmationInput():
    confirmed = getch.getch()
    if(confirmed == '1'):
        return True
    else:
        return waitForConfirmationInput()

def gameplayloop(board):
    vc = cv.VideoCapture(0)

    TextToSpeechEngine = tts.init()
    TextToSpeechEngine.setProperty("volume", 15)
    TextToSpeechEngine.setProperty("rate", 170)

    TextToSpeechEngine.say("Please confirm the board is clear before proceeding.")
    TextToSpeechEngine.runAndWait()
    print("Please confirm the board is clear before proceeding by pressing 1.")
    waitForConfirmationInput()
    #thinkTime = input("How long should I think per turn: ") #user can play as white or black, however for now it only works if white is at bottom of image and black is at top.

    TextToSpeechEngine.say("Select mode of play.")
    TextToSpeechEngine.runAndWait()
    print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")
    mode = getch.getch()


    TextToSpeechEngine.say("White or black?")
    TextToSpeechEngine.runAndWait()
    print("White or black? w or b: ")
    worB = getch.getch()

    # Capture image
    counter = 0
    while(counter < 5):
        ret,img = vc.read()
        counter += 1
    img = img[topleft[1]:bottomright[1], topleft[0]:bottomright[0]]
    cv.imwrite(img_path, img)

    topleft, bottomright = segmentation_analysis(image) #find the coordinates of the board within the camera frame

    mode_dict = {
        "e":1,
        "m":3,
        "h":5,
        "p":7
    }

    depth = mode_dict.get(mode)
    computerSide = ChessMatch(float(depth)) #set up our AI interface, initialised with a time it may process the board for

    firstImage = 'true'
    rotateImage = 'false'

    if(worB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make

            if (x == None):
                print("Congratulations! You won the game.")
                TextToSpeechEngine.say("Congratulations! You won the game.")
                TextToSpeechEngine.runAndWait()
                break
            else:
                board.push(x)
                #planSimple(str(x))
                print("AI makes move: {}.".format(x),"\n")
                print(board)
                stopNow = userTurn(board, computerSide, topleft, bottomright, 'b', TextToSpeechEngine, vc, firstImage, rotateImage)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'w', TextToSpeechEngine, vc, firstImage, rotateImage)
            print(board)
            if (not stopNow):
                computerSide.endgame()
                break
            x = computerSide.aiTurn()

            if (x == None):
                print("Congratulations! You won the game.")
                TextToSpeechEngine.say("Congratulations! You won the game.")
                TextToSpeechEngine.runAndWait()
                break
            else:
                board.push(x)
                #planSimple(str(x))
                print("AI makes move: {}.".format(x), "\n")
                print(board)

def main():
    board = chess.Board()
    gameplayloop(board)

if __name__ == '__main__':
    main()
