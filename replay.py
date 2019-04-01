import sys
import requests
from util.planner import *
from util.util import *
from dictionary import print_play, play_sound
from mainUserMoves import text_to_speech, waitForConfirmationInput
from classes.boardState import *
from classes.move import *

def main(lang, kasparov=False):
    moves = []
    boardState = BoardState()
    
    if (kasparov):
        # open file and read the content in a list
        with open('games/deep_blue_vs_kasparov.txt', 'r') as filehandle:
            moves = [current_place.rstrip() for current_place in filehandle.readlines()]
    else:
        # open file and read the content in a list
        with open('games/last.txt', 'r') as filehandle:
            moves = [current_place.rstrip() for current_place in filehandle.readlines()]
    
    if (len(moves) == 0):
        print_play("You haven't played any games yet.", lang)
        sys.exit()
    
    worB = " "
    
    print_play("Please start the calibration process. Refer to the instruction manual for help.", lang)
    print('started request')
    try:
        requests.post("http://192.168.105.110:8000/init", "POST")
    except requests.exceptions.ConnectionError:
        print_play("EV3 is not connected.", lang)
        sys.exit()
    print('finished request')
    print_play("Calibration completed successfully.", lang)
    
    assert("user" in moves[0])
    if (moves[0][5] == 'b'):
        worB = 'b'
        if (kasparov):
            print_play("Kasparov played with black.", lang)  
        else:    
            print_play("You played with black.", lang)        
        print_play("Please set up the board, placing the black pieces on your side. Confirm by pressing yes.", lang)
        waitForConfirmationInput()
    else:
        worB = 'w'
        print_play("You played with white.", lang)
        print_play("Please set up the board, placing the white pieces on your side. Confirm by pressing yes.", lang)
        waitForConfirmationInput()
    print(worB)
    for move in moves[1:]:
        moveDictFrom = squareToCoordinates(move[0:2], "w")
        moveDictTo   = squareToCoordinates(move[2:4], "w")
        moveObj = Move(moveDictFrom, moveDictTo)       
        fen = "/".join(boardState.state)
        print(move, fen)
        print(len(move))
        plan(move, lang, worB, board=fen, replay=True)
        boardState.applyMove(moveObj)
            
        if(len(move) == 5):
            if (lang == 'en'):    
                text_to_speech("Promotion! Please place the queen on {} and press yes".format(move[2:4]), lang)
            if (lang == 'es'):
                text_to_speech("¡Promoción! Por favor, coloque la reina en {} y presione Sí".format(move[2:4]), lang)
            if (lang == 'fr'):    
                text_to_speech("Promotion! Veuillez placer la reine sur {} et appuyer sur Oui".format(move[2:4]), lang)
            if (lang == 'de'):
                text_to_speech("Bauernumwandlung! Bitte setzen Sie die Dame auf {} und drücken Sie Ja.".format(move[2:4]), lang)
            if (lang == 'zh-cn'):    
                text_to_speech("升变！请将皇后放置到{}并按确认键。".format(move[2:4]), lang)
            
            waitForConfirmationInput()
                
if __name__ == '__main__':
    main("en")