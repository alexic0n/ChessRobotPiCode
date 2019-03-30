import sys
from util.planner import *
from util.util import *
from dictionary import print_play, play_sound
from mainUserMoves import text_to_speech, waitForConfirmationInput

def main(lang):
    moves = []
    
    # open file and read the content in a list
    with open('games/last.txt', 'r') as filehandle:
        moves = [current_place.rstrip() for current_place in filehandle.readlines()]
    
    if (len(moves) == 0):
        print_play("You haven't played any games yet.", lang)
        sys.exit()
    
    worB = " "
    for move in moves:
        if ('user' in move):
            if (move[5] == 'b'):
                worB = 'b'
                print_play("You played with black.", lang)
            else:
                worB = 'w'
                print_play("You played with white.", lang)
        else:
            print(move)
            print(len(move))
            plan(move, lang, worB)
            
            if(len(move) == 5):
                text_to_speech("Promotion! Please place the queen on {} and press yes when you are ready.".format(move[2:4]), lang)
                waitForConfirmationInput()
                
if __name__ == '__main__':
    main("en")