# import files like this
# from classes.boardState import *
# from classes.move import *
import sys
sys.path.append("./util/pythonchess")
import chess
import chess.engine
import cv2 as cv
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
mic_name = 'USB Device 0x46d:0x8b2: Audio (hw:1,0)'
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100# 44.1kHz sampling rate
chunk = 512 # 2^12 samples for buffer
record_secs = 4 # seconds to record
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

def userTurn(board, computerSide, topleft, bottomright, WorB, vc, firstImage, rotateImage, control): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print("Checkmate: Game Over!")
        play_sound('sounds/game_over.wav')
        return False
    if(board.is_check()):
        print("You are in check...save your king!")
        play_sound('sounds/check.wav')

    play_sound('sounds/move_user_button.wav')
        
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
            if (data['move'][-1] == 'q'):
                # Promotion
                move_str = data['move']
                print("You made promotion at {}. Is this correct?".format(move_str[2:4]))
                text_to_speech("You made promotion at {}. Is this correct?".format(move_str[2:4]))
                
                if (control == '2'):
                    is_correct = audio_to_text()[0].lower()
                else:
                    is_correct = waitForConfirmationInputYesNo()
                    
                if is_correct == 'y':
                    play_sound('sounds/promotion.wav')
                    print("You can only make queen promotion. Please place the queen on the desired square and press yes when you are done.")
                    waitForConfirmationInput()
                    
                    print(move_str)
                    move = chess.Move.from_uci(move_str)
                    board.push(move)
                    computerSide.userTurn(move)
                    return True
                
            else:    
                if (data['move'][2] == "a"):
                    # Queenside castling
                    play_sound('sounds/queenside_castling.wav')
                    print("You have made queenside castling. Is this correct? y or n")
                    if (control == '2'):
                        is_correct = audio_to_text()[0].lower()
                    else:
                        is_correct = waitForConfirmationInputYesNo()
                    if (is_correct == 'n'):
                        queenside = 'false'
    
                if (data['move'][2] == "h"):
                    # Kingside castling
                    play_sound('sounds/kingside_castling.wav')
                    print("You have made kingside castling. Is this correct? y or n")
                    if (control == '2'):
                        is_correct = audio_to_text()[0].lower()
                    else:
                        is_correct = waitForConfirmationInputYesNo()
                    if (is_correct == 'n'):
                        kingside = 'false'

        else:
            text_to_speech(data['status'] + ". Is this correct?")
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
                    text_to_speech("Have you moved a {} from {}?".format(piece, origin))
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
                            play_sound('sounds/legal_move.wav')
                            print('Are you sure that you made a legal move? y or n')
                            if (control == '2'):
                                is_legal = audio_to_text()[0].lower()
                            else:
                                is_legal = waitForConfirmationInputYesNo()

                            if is_legal == 'y':
                                probability_rank = str(int(data['probability_rank']) + 1)
                            else:
                                play_sound('sound/move_again_user.wav')
              
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
            play_sound('sounds/invalid_move.wav')
            print("Your move is invalid. Please make a new move and confirm it by pressing 1.")
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
    
def convertToFenWithSpaces(fen):
       boardState = fen.split(' ')[0]
       out = ""
       for char in boardState:
           if char in "12345678":
               out += "*" * int(char)
           else:
               out += char
       return out
    
def audio_to_text():    
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
        play_sound('sounds/start.wav')
        
        frames = []
        
        # loop through stream and append audio chunks to frame array
        for ii in range(0,int((samp_rate/chunk)*record_secs)):
            data = stream.read(chunk, exception_on_overflow = False)
            frames.append(data)
        
        print("finished recording")
        play_sound('sounds/end.wav')
        
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
        if (text == "Sorry, can you please repeat that?"):
            play_sound('sounds/repeat.wav')
            print(text)
    
    return text
    

def gameplayloop(board, control):
    #Initialize camera
    vc = cv.VideoCapture(1)

    play_sound('sounds/board_clear.wav')
    print("Please confirm the board is clear before proceeding by pressing 1.")
    waitForConfirmationInput()

    print("Select mode of play (e for easy, m for moderate, h for hard, p for pro):")
    
    if (control == '2'):
        play_sound('sounds/mode_of_play_speech.wav')
        mode = audio_to_text()[0].lower()
    else:
        play_sound('sounds/mode_of_play_button.wav')
        mode = getch.getch()
        
    mode_text_dict = {
        "e":'easy',
        "m":'moderate',
        "h":'hard',
        "p":'pro'
    }
    
    text_to_speech("You have selected {} mode.".format(mode_text_dict.get(mode, 'easy')))
    print("You have selected {} mode.".format(mode_text_dict.get(mode, 'easy')))

    print("White or black? w or b: ")
    
    if (control == '2'):
        play_sound('sounds/white_black_speech.wav')
        worB = audio_to_text()[0].lower()
    else:
        play_sound('sounds/white_black_button.wav')
        worB = getch.getch()
        
    if not (worB == 'w' or worB == 'b'):
        worB == 'w'
    if (worB == 'w'):
        play_sound('sounds/white.wav')
        print("You have selected white.")
    else:
        play_sound('sounds/black.wav') 
        print("You have selected black.")

    # Capture image
    counter = 0
    while(counter < 5):
        ret,image = vc.read()
        counter += 1
    
#    if (image == None):
#        play_sound('sounds/cam_not_detected.wav')
#        print("Unable to detect camera. Please unplug and plug it again.")
#        sys.exit()
    
    cv.imwrite("images/image.jpg",image)

    topleft, bottomright = segmentation_analysis(image) #find the coordinates of the board within the camera frame

    mode_dict = {
        "e":1,
        "m":3,
        "h":5,
        "p":7
    }

    depth = mode_dict.get(mode, 'easy')

    computerSide = ChessMatch(float(depth)) #set up our AI interface, initialised with a time it may process the board for

    firstImage = 'true'
    rotateImage = 'false'

    if(worB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make

            if (x == None):
                print("Congratulations! You won the game.")
                play_sound('sounds/won.wav')
                break
            else:
                fen_parts = board.fen().split(" ")
                board.push(x)
                fen = convertToFenWithSpaces(fen_parts[0])
                enpassant = fen_parts[3]
                
                if(not str(x)[-1].isdigit()):
                    x = str(x)[0:4]
                    
                plan(str(x), fen, enpassant)
                
                if(str(x) == 'e1h1' or str(x) == 'e1g1'):
                    print("I made kingside castling. Your turn!")
                    play_sound('sounds/robot_kingside_castling.wav')
                    
                elif(str(x) == 'e1a1' or str(x) == 'e1c1'):
                    print("I made queenside castling. Your turn!")
                    play_sound('sounds/robot_kingside_castling.wav')
                    
                elif(not str(x)[-1].isdigit()):
                    prom_dict = {
                        "q":"queen",
                        "n":"knight",
                        "r":"rook",
                        "b":"bishop"
                    }
                    piece = str(x)[-1].lower()
                    print("I made {} promotion. Your turn!".format(prom_dict.get(piece)))
                    text_to_speech("I made {} promotion. Your turn!".format(prom_dict.get(piece)))
                  
                else:    
                    text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]))
                    print("AI makes move: {}.".format(x),"\n")
                
                print(board)
                stopNow = userTurn(board, computerSide, topleft, bottomright, 'b', vc, firstImage, rotateImage, control)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'w', vc, firstImage, rotateImage, control)
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
                fen_parts = board.fen().split(" ")
                board.push(x)
                fen = convertToFenWithSpaces(fen_parts[0])
                enpassant = fen_parts[3]
                
                if(not str(x)[-1].isdigit()):
                    x = str(x)[0:4]
                    
                plan(str(x), fen, enpassant)
                
                if(str(x) == 'e8h8' or str(x) == 'e8g8'):
                    print("I made kingside castling. Your turn!")
                    play_sound('sounds/robot_kingside_castling.wav')
                    
                elif(str(x) == 'e8a8' or str(x) == 'e8c8'):
                    print("I made queenside castling. Your turn!")
                    play_sound('sounds/robot_queenside_castling.wav')
                    
                elif(not str(x)[-1].isdigit()):
                    prom_dict = {
                        "q":"queen",
                        "n":"knight",
                        "r":"rook",
                        "b":"bishop"
                    }
                    piece = str(x)[-1].lower()
                    print("I made {} promotion. Your turn!".format(prom_dict.get(piece)))
                    text_to_speech("I made {} promotion. Your turn!".format(prom_dict.get(piece)))
                  
                else:    
                    text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]))
                    print("AI makes move: {}.".format(x), "\n")
                
                print(board)

def main():
    control = '2'
    board = chess.Board()
    
    gameplayloop(board, control)

if __name__ == '__main__':
    main()
