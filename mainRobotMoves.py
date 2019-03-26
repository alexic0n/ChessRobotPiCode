# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("./util/pythonchess")
import chess
import chess.engine
import getch
import pyaudio
import wave

sys.path.append("./")
from classes.aiInterface import *
from util.util import *
from util.planner import *
import requests
import json

# Audio settings
mic_name = 'USB Device 0x46d:0x8b2: Audio (hw:1,0)'
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100# 44.1kHz sampling rate
chunk = 512 # 2^12 samples for buffer
record_secs = 5 # seconds to record
wav_output_filename = 'audio.wav' # name of .wav file

def play_sound(path):
    #define stream chunk   
    chunk = 1024  
    
    #open a wav format music  
    f = wave.open(path)  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  
    
    #play stream  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  
    
    #stop stream  
    stream.stop_stream()  
    stream.close()  
    
    #close PyAudio  
    p.terminate()
    
def text_to_speech(text):
    r = requests.post("http://www.checkmate.tardis.ed.ac.uk/text_to_speech", files={
            'text': text,
        })

    with wave.open('sounds/audio.wav','wb') as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(26500)
            file.writeframes(r.content)
    
    play_sound('sounds/audio.wav')

def userTurn(board, computerSide): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        play_sound('sounds/game_over.wav')
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
        play_sound('sounds/check.wav')
    
    play_sound('sounds/move_robot.wav')
    print("Please choose your next move and press 1 when you are ready to announce it.")
    waitForConfirmationInput()
    
    legalMoves = getLegalMoves(board)
    
    while(True):
        move_str = audio_to_text(True)
        
        if (move_str in legalMoves):
            text_to_speech("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
            print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
            text = audio_to_text(False)[0]
            if (text == 'n'):
                play_sound('sounds/move_again_robot.wav')
                print("Please press 1 again when you are ready to announce your move.")
                waitForConfirmationInput()
            else:
                move = chess.Move.from_uci(move_str)
                board.push(move)
                computerSide.userTurn(move)
                #planSimple(move_str)
                return True
        else:
            text_to_speech("I detected {} to {}. This is an illegal move. Please press yes again, when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            print("I detected {} to {}. This is an illegal move. Please press 1 again when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            waitForConfirmationInput()
    
def checkIfSquare(s):
    return (len(s) == 2 and s[0].isalpha() and s[1].isdigit())

def getLegalMoves(board):
    x = board.legal_moves
    legalMoves = []
    for move in x:
        legalMoves.append(str(move))
    return legalMoves

def waitForConfirmationInputYesNo():
    choice = getch.getch()
    if (choice == 'q'):
        sys.exit()
    return choice

def waitForConfirmationInput():
    confirmed = getch.getch()
    if(confirmed == '1'):
        return True
    elif(confirmed =='q'):
        sys.exit()
    else:
        return waitForConfirmationInput()
    
def audio_to_text(recogniseMove):
    text = "Sorry, can you please repeat that?"
    
    while (text == "Sorry, can you please repeat that?"):
        #Initalize microphone
        audio = pyaudio.PyAudio()
        
        dev_index = -1
        for ii in range(audio.get_device_count()):
            name = audio.get_device_info_by_index(ii).get('name')
            if (name == mic_name):
                dev_index = ii 
            
        if (dev_index == -1):
            play_sound('sounds/mic_not_detected.wav')
            print("Unable to detect microphone. Please unplug and plug it again.")
            sys.exit()
        
        # create pyaudio stream
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
        
        print("recording")
        play_sound('sounds/beep.wav')
        
        frames = []
        
        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk, exception_on_overflow = False)
            frames.append(data)
        
        print("finished recording")
        play_sound('sounds/beep.wav')
        
        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # save the audio frames as .wav file
        wavefile = wave.open(wav_output_filename,'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()
        
        r = requests.post("http://www.checkmate.tardis.ed.ac.uk/speech_recognition", files={
            'user_speech': open('audio.wav', 'rb'),
        })
        
        data = r.json()
        
        text = data['text']
        if (text == "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead."):
            play_sound('sounds/server_down.wav')
            print(text)
            sys.exit()
        if (text == "Sorry, can you please repeat that?" and recogniseMove == False):
            play_sound('sounds/repeat.wav')
            print(text)
            
        if (recogniseMove == True):
            words = text.split(" ")
            if not (len(words) == 4):
                text = "Sorry, can you please repeat that?"
                play_sound('sounds/repeat.wav')
                print(text)
            else:
                text = words[0] + words[2]
    return text
    

def gameplayloop(board):
    play_sound('sounds/board_clear.wav')
    print("Please confirm the board is clear before proceeding by pressing 1.")
    waitForConfirmationInput()

    play_sound('sounds/mode_of_play_speech.wav')
    print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")

    mode = audio_to_text(False)[0].lower()
    
    mode_text_dict = {
        "e":'easy',
        "m":'moderate',
        "h":'hard',
        "p":'pro'
    }
    
    text_to_speech("You have selected {} mode.".format(mode_text_dict.get(mode, 'easy')))
    print("You have selected {} mode.".format(mode_text_dict.get(mode, 'easy')))

    play_sound('sounds/white_black_speech.wav')
    print("White or black? w or b: ")
    
    worB = audio_to_text(False)[0].lower()
    
    if not (worB == 'w' or worB == 'b'):
        worB == 'w'
    if (worB == 'w'):
        play_sound('sounds/white.wav')
        print("You have selected white.")
    else:
        play_sound('sounds/black.wav') 
        print("You have selected black.")

    mode_dict = {
        "e":1,
        "m":3,
        "h":5,
        "p":7
    }

    depth = mode_dict.get(mode, 1)
    computerSide = ChessMatch(float(depth)) #set up our AI interface, initialised with a time it may process the board for

    if(worB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make

            if (x == None):
                print("Congratulations! You won the game.")
                play_sound('sounds/won.wav')
                break
            else:
                board.push(x)
                #planSimple(str(x))
                text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]))
                print("AI makes move: {}.".format(x),"\n")
                print(board)
                stopNow = userTurn(board, computerSide)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide)
            print(board)
            if (not stopNow):
                computerSide.endgame()
                break
            x = computerSide.aiTurn()

            if (x == None):
                print("Congratulations! You won the game.")
                play_sound('sounds/won.wav')
                break
            else:
                board.push(x)
                #planSimple(str(x))
                text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]))
                print("AI makes move: {}.".format(x), "\n")
                print(board)

def main():
    board = chess.Board()
    
    gameplayloop(board)

if __name__ == '__main__':
    main()
