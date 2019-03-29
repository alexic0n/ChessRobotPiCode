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
from util.storeMoves import storeMoves
import requests
import json
from crop import crop_squares
from dictionary import print_play, play_sound

img_path = "images/image.jpg"

# Audio settings
mic_name = 'USB Device 0x46d:0x8b2: Audio (hw:1,0)'
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100# 44.1kHz sampling rate
chunk = 512 # 2^12 samples for buffer
record_secs = 4 # seconds to record
wav_output_filename = 'audio.wav' # name of .wav file

def text_to_speech(text, lang):
    r = requests.post("http://www.checkmate.tardis.ed.ac.uk/text_to_speech", files={
            'text': text,
            'lang': lang
        })

    with wave.open('sounds/audio.wav','wb') as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(26500)
            file.writeframes(r.content)
    
    play_sound('sounds/audio.wav')

def userTurn(board, computerSide, topleft, bottomright, WorB, vc, firstImage, rotateImage, control, lang, storeMovesList): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print_play("Checkmate: Game Over!", lang)
        storeMovesList.save()
        return False
    if(board.is_check()):
        print_play("You are in check...save your king!", lang)
        
    print_play("Make your move on the board. Confirm by pressing 1.", lang)
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
                if (lang == 'en'):
                    print("You made promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("You made promotion at {}. Is this correct?".format(move_str[2:4]), lang)
                if (lang == 'es'):
                    pass
                if (lang == 'fr'):
                    print("You made promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("Vous avez fait une promotion en {}. Est-ce correct?".format(move_str[2:4]), lang)
                if (lang == 'de'):
                    print("You made promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("Sie haben eine Umwandlung auf {} gemacht, ist das richtig?".format(move_str[2:4]), lang)
                if (lang == 'zh-cn'):
                    print("You made promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("您是否升变了{}?".format(move_str[2:4]), lang)
                    
                
                if (control == '2'):
                    is_correct = audio_to_text(lang)[0].lower()
                else:
                    is_correct = waitForConfirmationInputYesNo()
                    
                if is_correct == 'y':
                    print_play("You can only make queen promotion. Please place the queen on the desired square and press yes when you are done.", lang)
                    waitForConfirmationInput()
                    
                    print(move_str)
                    move = chess.Move.from_uci(move_str)
                    board.push(move)
                    computerSide.userTurn(move)
                    
                    # Store move
                    storeMovesList.add(move_str)
                    
                    return True
                
            else:    
                if (data['move'][2] == "a"):
                    # Queenside castling
                    print_play("You have made queenside castling. Is this correct? y or n", lang)
                    if (control == '2'):
                        is_correct = audio_to_text(lang)[0].lower()
                    else:
                        is_correct = waitForConfirmationInputYesNo()
                    if (is_correct == 'n'):
                        queenside = 'false'
    
                if (data['move'][2] == "h"):
                    # Kingside castling
                    print_play("You have made kingside castling. Is this correct? y or n", lang)
                    if (control == '2'):
                        is_correct = audio_to_text(lang)[0].lower()
                    else:
                        is_correct = waitForConfirmationInputYesNo()
                    if (is_correct == 'n'):
                        kingside = 'false'

        else:
            if (lang == 'en'):
                text_to_speech(data['status'] + ". Is this correct?", lang)
                print(data['status'] + ". Is this correct? y or n")
            if (lang == 'es'):
                pass
            if (lang == 'fr'):
                text_to_speech(data['status'] + ". Est-ce correct?", lang)
                print(data['status'] + ". Is this correct? y or n")
            if (lang == 'de'):
                text_to_speech(data['status'] + ". Ist das richtig?", lang)
                print(data['status'] + ". Is this correct? y or n")
            if (lang == 'zh-cn'):
                text_to_speech(data['status'] + "。对吗？", lang)
                print(data['status'] + ". Is this correct? y or n")
                
            if (control == '2'):
                is_correct = audio_to_text(lang)[0].lower()
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
            
            # Store moves
            storeMovesList.add(move_str)
            
            return True

        else:
            # NEXT PROBABLE MOVE
            if not originKnown:
                status_list = data['status'].split(" ")
                piece = status_list[0]
                
                dict_piece_fr = {
                    'Pawn':'pion',
                    'Bishop':'fou',
                    'Rook':'tour',
                    'Queen':'dame',
                    'King':'roi',
                    'Knight':'cavalier'
                }
                
                dict_piece_de = {
                    'Pawn':'Bauer',
                    'Bishop':'Läufer',
                    'Rook':'Turm',
                    'Queen':'Dame',
                    'King':'König',
                    'Knight':'Springer'
                }
                
                dict_piece_zh_cn = {
                    'Pawn':'士兵',
                    'Bishop':'主教',
                    'Rook':'城堡',
                    'Queen':'王后',
                    'King':'国王',
                    'Knight':'骑士'
                }
                
                origin = status_list[3]
                if not (len(data['move']) == 5):
                    if (lang == 'en'):
                        text_to_speech("Have you moved a {} from {}?".format(piece, origin), lang)
                        print("Have you moved a {} from {}? y or n".format(piece, origin))
                    if (lang == 'es'):
                        pass
                    if (lang == 'fr'):
                        text_to_speech("Avez-vous déplacé un {} de {}?".format(piece, origin), lang)
                        print("Have you moved a {} from {}? y or n".format(piece, origin))
                    if (lang == 'de'):
                        text_to_speech("Haben Sie {} von {} verschoben?".format(dict_piece_de.get(piece), origin), lang)
                        print("Have you moved a {} from {}? y or n".format(piece, origin))
                    if (lang == 'zh-cn'):
                        text_to_speech("您是否刚刚移动了{} 上的{}".format(origin, piece), lang)
                        print("Have you moved a {} from {}? y or n".format(dict_piece_zh_cn.get(piece), origin))
                
                    
                    if (control == '2'):
                        is_origin = audio_to_text(lang)[0].lower()
                    else:
                        is_origin = waitForConfirmationInputYesNo()
                        
                    if (is_origin == 'y'):
                        originKnown = True
                        currentLegalMoves = [move for move in currentLegalMoves if not move == data['move'] and move[0:2] == origin]
                    else:
                        incorrect_count = incorrect_count + 1
                        if incorrect_count == 2:
                            print_play('Are you sure that you made a legal move? y or n', lang)
                            if (control == '2'):
                                is_legal = audio_to_text(lang)[0].lower()
                            else:
                                is_legal = waitForConfirmationInputYesNo()

                            if is_legal == 'y':
                                probability_rank = str(int(data['probability_rank']) + 1)
                            else:
                                print_play("Please make a new move. Press 1 to confirm.", lang)
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
            print_play("Your move is invalid. Please make a new move and confirm it by pressing 1.", lang)
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
    
def audio_to_text(lang):    
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
            print_play("Unable to detect microphone. Please unplug and plug it again.", lang)
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
            'lang': lang
        })
        
        data = r.json()
        
        text = data['text']
        if (text == "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead."):
            print_play(text, lang)
            sys.exit()
        if (text == "Sorry, can you please repeat that?"):
            print_play(text, lang)
    
    return text
    

def gameplayloop(board, control, lang):
    #Initialize camera
    vc = cv.VideoCapture(1)
    
    #Initialize storeMoves class
    storeMovesList = storeMoves()

    print_play("Please confirm the board is clear before proceeding by pressing 1.", lang)
    waitForConfirmationInput()

    print_play(control + '.' + "Select mode of play (e for easy, m for moderate, h for hard, p for pro):", lang)
    if (control == '2'):
        mode = audio_to_text(lang)[0].lower()
    else:
        mode = getch.getch()
        
    mode_text_dict_en = {
        "e":'easy',
        "m":'moderate',
        "h":'hard',
        "p":'pro'
    }
    
    mode_text_dict_fr = {
        "e":'facile',
        "m":'modéré',
        "h":'difficile',
        "p":'pro'
    }
    
    mode_text_dict_de = {
        "e":'einfachen',
        "m":'mittleren',
        "h":'harten',
        "p":'Pro-Modus'
    }
    
    mode_text_dict_zh_cn = {
        "e":'简单',
        "m":'中等',
        "h":'困难',
        "p":'专家'
    }
    
    
    if (lang == 'en'):
        text_to_speech("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))
    if (lang == 'es'):
        pass
    if (lang == 'fr'):
        text_to_speech("Vous avez sélectionné le mode {}.".format(mode_text_dict_fr.get(mode, 'facile')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))
    if (lang == 'de'):
        text_to_speech("Sie haben den {} ausgewählt.".format(mode_text_dict_de.get(mode, 'einfachen')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))
    if (lang == 'zh-cn'):
        text_to_speech("您选择了{} 模式。".format(mode_text_dict_zh_cn.get(mode, '简单')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))

    print_play(control + '.' + "White or black? w or b: ", lang)
    
    if (control == '2'):
        worB = audio_to_text(lang)[0].lower()
    else:
        worB = getch.getch()
        
    if not (worB == 'w' or worB == 'b'):
        worB == 'w'
    if (worB == 'w'):
        print_play("You have selected white.", lang)
    else:
        print_play("You have selected black.", lang)

    storeMovesList.add('user:' + worB)

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
    
    prom_dict_en = {
        "q":"queen",
        "n":"knight",
        "r":"rook",
        "b":"bishop"
    }
    
    prom_dict_fr = {
        "q":"dame",
        "n":"cavalier",
        "r":"tour",
        "b":"fou"
    }
    
    prom_dict_de = {
        "q":"Dame",
        "n":"Springer",
        "r":"Turm",
        "b":"Läufer"
    }
    
    prom_dict_zh_cn = {
        "q":"王后",
        "n":"骑士",
        "r":"城堡",
        "b":"主教"
    }

    if(worB == 'b'): #run the game recursively until the user quits or checkmate is achieved
        while(True):
            x = computerSide.aiTurn() #obtain the move the ai would make

            if (x == None):
                print_play("Congratulations! You won the game.", lang)
                storeMovesList.save()
                break
            else:
                fen_parts = board.fen().split(" ")
                board.push(x)
                fen = convertToFenWithSpaces(fen_parts[0])
                enpassant = fen_parts[3]
                
                # Store moves
                storeMovesList.add(str(x))
                
                if(not str(x)[-1].isdigit()):
                    x = str(x)[0:4]
                    
                plan(str(x), lang, fen, enpassant)
                
                if(str(x) == 'e1h1' or str(x) == 'e1g1'):
                    print_play("I made kingside castling. Your turn!", lang)
                    
                elif(str(x) == 'e1a1' or str(x) == 'e1c1'):
                    print_play("I made queenside castling. Your turn!", lang)
                    
                elif(not str(x)[-1].isdigit()):
                    piece = str(x)[-1].lower()
                    if (lang == 'en'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)), lang)
                    if (lang == 'es'):
                        pass
                    if (lang == 'fr'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("J'ai fait la promotion de la {}. À votre tour!".format(prom_dict_fr.get(piece)), lang)
                    if (lang == 'de'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("Ich habe eine Umwandlung auf {} gemacht. Du bist dran!".format(prom_dict_de.get(piece)), lang)
                    if (lang == 'zh-cn'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("I made {} promotion. Your turn!".format(prom_dict_zh_cn.get(piece)), lang)
                  
                else:    
                    if (lang == 'en'):
                        text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'es'):
                        pass
                    if (lang == 'fr'):
                        text_to_speech("Je me suis déplacé de {} à {}. À votre tour!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'de'):
                        text_to_speech("Ich bin von {} nach {} gezogen. Du bist dran.".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'zh-cn'):
                        text_to_speech("我从{}移动到{}，到你了。".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                
                print(board)
                stopNow = userTurn(board, computerSide, topleft, bottomright, 'b', vc, firstImage, rotateImage, control, lang, storeMovesList)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, topleft, bottomright, 'w', vc, firstImage, rotateImage, control, lang, storeMovesList)
            print(board)
            if (not stopNow):
                computerSide.endgame()
                break
            x = computerSide.aiTurn()

            if (x == None):
                print_play("Congratulations! You won the game.", lang)
                storeMovesList.save()
                break
            else:
                fen_parts = board.fen().split(" ")
                board.push(x)
                fen = convertToFenWithSpaces(fen_parts[0])
                enpassant = fen_parts[3]
                
                # Store moves
                storeMovesList.add(str(x))
                
                if(not str(x)[-1].isdigit()):
                    x = str(x)[0:4]
                    
                plan(str(x), lang, fen, enpassant)
                
                if(str(x) == 'e8h8' or str(x) == 'e8g8'):
                    print_play("I made kingside castling. Your turn!", lang)
                    
                elif(str(x) == 'e8a8' or str(x) == 'e8c8'):
                    print_play("I made queenside castling. Your turn!", lang)
                    
                elif(not str(x)[-1].isdigit()):
                    piece = str(x)[-1].lower()
                    if (lang == 'en'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)), lang)
                    if (lang == 'es'):
                        pass
                    if (lang == 'fr'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("J'ai fait la promotion de la {}. À votre tour!".format(prom_dict_fr.get(piece)), lang)
                    if (lang == 'de'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("Ich habe eine Umwandlung auf {} gemacht. Du bist dran!".format(prom_dict_de.get(piece)), lang)
                    if (lang == 'zh-cn'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("I made {} promotion. Your turn!".format(prom_dict_zh_cn.get(piece)), lang)
                  
                else:    
                    if (lang == 'en'):
                        text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'es'):
                        pass
                    if (lang == 'fr'):
                        text_to_speech("Je me suis déplacé de {} à {}. À votre tour!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'de'):
                        text_to_speech("Ich bin von {} nach {} gezogen. Du bist dran.".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'zh-cn'):
                        text_to_speech("我从{}移动到{}，到你了。".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                
                print(board)

def main(control, lang):
    board = chess.Board()
    
    gameplayloop(board, control, lang)

if __name__ == '__main__':
    main()
