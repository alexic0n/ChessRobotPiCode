import sys
from util.planner import *
from util.util import *
from dictionary import print_play, play_sound
from mainUserMoves import text_to_speech, waitForConfirmationInput
from classes.boardState import *
from classes.move import *

def main(lang):
    moves = []
    boardState = BoardState()
    
    # open file and read the content in a list
    with open('games/last.txt', 'r') as filehandle:
        moves = [current_place.rstrip() for current_place in filehandle.readlines()]
    
    if (len(moves) == 0):
        print_play("You haven't played any games yet.", lang)
        sys.exit()
    
    worB = " "
    assert("user" in moves[0])
    if (moves[0][5] == 'b'):
        worB = 'b'
        print_play("You played with black.", lang)
    else:
        worB = 'w'
        print_play("You played with white.", lang)
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