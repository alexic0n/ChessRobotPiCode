from dictionary import print_play, play_sound, waitForConfirmationInput, play_sound_pyaudio
import requests
import sys
from mainUserMoves import convertToFenWithSpaces, userTurn as userTurnKeyboard, text_to_speech
from mainRobotMoves import userTurn as userTurnVoice
sys.path.append("./util/pythonchess")
import chess
import chess.engine
from classes.aiInterface import *
from classes.segmentation_analysis import *
from util.planner import plan
import cv2 as cv
from util.storeMoves import storeMoves
import time
import pygame

LANG = 'en'
DIFF = 1
COLOUR = 'b'

#Initialize camera
vc = cv.VideoCapture(1)

def segment_image():
    # Capture image
    counter = 0
    while(counter < 5):
        ret,image = vc.read()
        counter += 1
        
    cv.imwrite("images/image.jpg",image)
    topleft, bottomright = segmentation_analysis(image) #find the coordinates of the board within the camera frame
    return topleft, bottomright

def demo():
    play_sound_pyaudio('sounds/startup.wav')
    
    KEYBOARD = True
    board = chess.Board()
    computerSide = ChessMatch(float(DIFF)) #set up our AI interface, initialised with a time it may process the board for
    storeMovesList = storeMoves()
    
    # Calibration
#    print_play("Please start the calibration process. Refer to the instruction manual for help.", LANG)
#    print('started request')
#    try:
#        requests.post("http://ev3:8000/init", "POST")
#    except requests.exceptions.ConnectionError:
#        print_play("EV3 is not connected.", LANG)
#        sys.exit()
#    print('finished request')
#    print_play("Calibration completed successfully.", LANG)
    
    print_play("Please set up the board, placing the black pieces on your side. Confirm by pressing yes.", LANG)
    waitForConfirmationInput()
    
    topleft, bottomright = segment_image()
    
    while(True):
        x = computerSide.aiTurn() #obtain the move the ai would make

        fen_parts = board.fen().split(" ")
        board.push(x)
    
        fen = convertToFenWithSpaces(fen_parts[0])
        enpassant = fen_parts[3] 
            
        text_to_speech("I'm moving {} to {}.".format(str(x)[0:2], str(x)[2:4]), LANG, False)      
        plan(str(x), LANG,  COLOUR, fen, enpassant)
        
        if(str(x) == 'e1h1' or str(x) == 'e1g1'):
            print_play("I made kingside castling. Your turn!", LANG, True)    
        elif(str(x) == 'e1a1' or str(x) == 'e1c1'):
            print_play("I made queenside castling. Your turn!", LANG, True)
        else:
            print('tts')
            text_to_speech("Your turn!", LANG)
            print("AI makes move: {}.".format(x),"\n")
        
        print(board)
        
        print(KEYBOARD)
        if KEYBOARD:
            stopNow = userTurnKeyboard(board, computerSide, topleft, bottomright, COLOUR, vc, False, False, '1', LANG, storeMovesList)
            KEYBOARD = False
        else:
            stopNow = userTurnVoice(board, computerSide, COLOUR, LANG, storeMovesList)
            KEYBOARD = True
        print(board)
        if(not stopNow):
            computerSide.endgame()
            break

    

if __name__ == '__main__':
    demo()