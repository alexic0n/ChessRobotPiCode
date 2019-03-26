# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("./util/pythonchess")
import chess
import chess.engine
import pyttsx3 as tts
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
record_secs = 4 # seconds to record
wav_output_filename = 'audio.wav' # name of .wav file

def userTurn(board, computerSide, TextToSpeechEngine): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        TextToSpeechEngine.say("Checkmate: Game Over!")
        TextToSpeechEngine.runAndWait()
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
        TextToSpeechEngine.say("You are in check...save your king!")
        TextToSpeechEngine.runAndWait()
    
    TextToSpeechEngine.say("Please choose your next move and press 1 when you are ready to announce it.")
    TextToSpeechEngine.runAndWait()
    print("Please choose your next move and press 1 when you are ready to announce it.")
    waitForConfirmationInput()
    
    legalMoves = getLegalMoves(board)
    
    while(True):
        move_str = audio_to_text(TextToSpeechEngine, True)
        
        if (move_str in legalMoves):
            TextToSpeechEngine.say("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
            TextToSpeechEngine.runAndWait()
            print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
            text = audio_to_text(TextToSpeechEngine, False)[0]
            if (text == 'n'):
                TextToSpeechEngine.say("Please press 1 again when you are ready to announce your move.")
                TextToSpeechEngine.runAndWait()
                print("Please press 1 again when you are ready to announce your move.")
            else:
                move = chess.Move.from_uci(move_str)
                board.push(move)
                computerSide.userTurn(move)
                #planSimple(move_str)
                return True
        else:
            TextToSpeechEngine.say("I detected {} to {}. This is an illegal move. Please press 1 again when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            TextToSpeechEngine.runAndWait()
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
    
def audio_to_text(TextToSpeechEngine, recogniseMove):
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
            TextToSpeechEngine.say("Unable to detect microphone. Please unplug and plug it again.")
            TextToSpeechEngine.runAndWait()
            print("Unable to detect microphone. Please unplug and plug it again.")
            sys.exit()
        
        print(form_1, samp_rate, chans, dev_index, chunk)
        # create pyaudio stream
        stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                            input_device_index = dev_index,input = True, \
                            frames_per_buffer=chunk)
        print("recording")
        frames = []
        
        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk)
            frames.append(data)
        
        print("finished recording")
        
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
            TextToSpeechEngine.say("Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead.")
            TextToSpeechEngine.runAndWait()
            print(text)
            sys.exit()
        if (text == "Sorry, can you please repeat that?"):
            TextToSpeechEngine.say("Sorry, can you please repeat that?")
            TextToSpeechEngine.runAndWait()
            print(text)
            
        if (recogniseMove == True):
            words = text.split(" ")
            if not (len(words) == 4):
                text = "Sorry, can you please repeat that?"
                TextToSpeechEngine.say("Sorry, can you please repeat that?")
                TextToSpeechEngine.runAndWait()
                print(text)
            else:
                text = words[0] + words[2]
    return text
    

def gameplayloop(board):
    TextToSpeechEngine = tts.init()
    TextToSpeechEngine.setProperty("volume", 15)
    TextToSpeechEngine.setProperty("rate", 170)

    TextToSpeechEngine.say("Please confirm the board is clear before proceeding.")
    TextToSpeechEngine.runAndWait()
    print("Please confirm the board is clear before proceeding by pressing 1.")
    waitForConfirmationInput()

    TextToSpeechEngine.say("Select mode of play.")
    TextToSpeechEngine.runAndWait()    
    print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")

    mode = audio_to_text(TextToSpeechEngine, False)[0].lower()
    
    mode_text_dict = {
        "e":'easy',
        "m":'moderate',
        "h":'hard',
        "p":'pro'
    }
    
    TextToSpeechEngine.say("You have selected {} mode.".format(mode_text_dict.get(mode, 'easy')))
    TextToSpeechEngine.runAndWait()
    print("You have selected {} mode.".format(mode_text_dict.get(mode, 'easy')))

    TextToSpeechEngine.say("White or black?")
    TextToSpeechEngine.runAndWait()
    print("White or black? w or b: ")
    
    worB = audio_to_text(TextToSpeechEngine, False)[0].lower()
    
    if not (worB == 'w' or worB == 'b'):
        worB == 'w'
    if (worB == 'w'):
        TextToSpeechEngine.say("You have selected white.")
        TextToSpeechEngine.runAndWait()    
        print("You have selected white.")
    else:
        TextToSpeechEngine.say("You have selected black.")
        TextToSpeechEngine.runAndWait()    
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
                TextToSpeechEngine.say("Congratulations! You won the game.")
                TextToSpeechEngine.runAndWait()
                break
            else:
                board.push(x)
                #planSimple(str(x))
                TextToSpeechEngine.say("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]))
                TextToSpeechEngine.runAndWait()
                print("AI makes move: {}.".format(x),"\n")
                print(board)
                stopNow = userTurn(board, computerSide, TextToSpeechEngine)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, TextToSpeechEngine)
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
                TextToSpeechEngine.say("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]))
                TextToSpeechEngine.runAndWait()
                print("AI makes move: {}.".format(x), "\n")
                print(board)

def main():
    board = chess.Board()
    
    gameplayloop(board)

if __name__ == '__main__':
    main()
