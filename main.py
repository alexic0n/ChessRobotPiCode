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
import pyaudio
import wave

sys.path.append("./")
from classes.aiInterface import *
from classes.segmentation_analysis import *
from util.util import *
from util.planner import *
import requests
import json
from crop import crop_squares

img_path = "images/image.jpg"

# Audio settings
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 16000# 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
record_secs = 6 # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'audio.wav' # name of .wav file

def userTurn(board, computerSide, topleft, bottomright, WorB, TextToSpeechEngine, vc, firstImage, rotateImage, control): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        TextToSpeechEngine.say("Checkmate: Game Over!")
        TextToSpeechEngine.runAndWait()
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
        TextToSpeechEngine.say("You are in check...save your king!")
        TextToSpeechEngine.runAndWait()

    TextToSpeechEngine.say("Make your move on the board. Confirm by pressing 1")
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
                if (control == '2'):
                    is_correct = audio_to_text()[0].lower()
                else:
                    is_correct = waitForConfirmationInputYesNo()
                if (is_correct == 'n'):
                    queenside = 'false'

            if (data['move'][2] == "h"):
                # Kingside castling
                TextToSpeechEngine.say("You have made kingside castling. Is this correct?")
                TextToSpeechEngine.runAndWait()
                print("You have made kingside castling. Is this correct? y or n")
                if (control == '2'):
                    is_correct = audio_to_text()[0].lower()
                else:
                    is_correct = waitForConfirmationInputYesNo()
                if (is_correct == 'n'):
                    kingside = 'false'

        else:
            TextToSpeechEngine.say(data['status'] + ". Is this correct?")
            TextToSpeechEngine.runAndWait()
            print(data['status'] + ". Is this correct? y or n")
            if (control == '2'):
                is_correct = audio_to_text()[0].lower()
            else:
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
                    
                    if (control == '2'):
                        is_origin = audio_to_text()[0].lower()
                    else:
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
                            if (control == '2'):
                                is_legal = audio_to_text()[0].lower()
                            else:
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
    
def audio_to_text():
    #Initalize microphone
    audio = pyaudio.PyAudio()
    
    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []
    
    # loop through stream and append audio chunks to frame array
    for ii in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(chunk, exception_on_overflow = False)
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
    
    return data['text']
    

def gameplayloop(board):
    #Initialize camera
    vc = cv.VideoCapture(0)

    TextToSpeechEngine = tts.init()
    TextToSpeechEngine.setProperty("volume", 15)
    TextToSpeechEngine.setProperty("rate", 170)

    TextToSpeechEngine.say("Please confirm the board is clear before proceeding.")
    TextToSpeechEngine.runAndWait()
    print("Please confirm the board is clear before proceeding by pressing 1.")
    waitForConfirmationInput()

    TextToSpeechEngine.say("Select 1 for keyboard control. Select 2 for voice control.")
    TextToSpeechEngine.runAndWait()    
    print("Select 1 for keyboard control. Select 2 for voice control.")
    control = getch.getch()

    TextToSpeechEngine.say("Select mode of play.")
    TextToSpeechEngine.runAndWait()    
    print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")
    
    if (control == '2'):
        mode = audio_to_text()[0].lower()
    else:
        mode = getch.getch()

    TextToSpeechEngine.say("White or black?")
    TextToSpeechEngine.runAndWait()
    print("White or black? w or b: ")
    
    if (control == '2'):
        worB = audio_to_text()[0].lower()
    else:
        worB = getch.getch()

    # Capture image
    counter = 0
    while(counter < 5):
        ret,image = vc.read()
        counter += 1

    cv.imwrite("images/image.jpg",image)

    # Take last image from the webcam
    #paths = glob.glob('images/*.jpg')
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
                stopNow = userTurn(board, computerSide, topleft, bottomright, 'b', TextToSpeechEngine, vc, firstImage, rotateImage, control)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'w', TextToSpeechEngine, vc, firstImage, rotateImage, control)
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
