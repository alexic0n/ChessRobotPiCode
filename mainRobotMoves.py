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
from util.storeMoves import storeMoves
from util.planner import *
import requests
import json
from dictionary import print_play, play_sound

# Audio settings
mic_name = 'USB Device 0x46d:0x8b2: Audio'
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100# 44.1kHz sampling rate
chunk = 512 # 2^12 samples for buffer
record_secs = 5 # seconds to record
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
    
def convertToFenWithSpaces(fen):
       boardState = fen.split(' ')[0]
       out = ""
       for char in boardState:
           if char in "12345678":
               out += "*" * int(char)
           else:
               out += char
       return out

def userTurn(board, computerSide, worB, lang, storeMovesList): #this basically just handles user interaction, reading the boardstate and update the internal board accordingly
    if(board.legal_moves.count() == 0):
        print_play("Checkmate: Game Over!", lang)
        storeMovesList.save()
        return False
    if(board.is_check()):
        print_play("You are in check...save your king!", lang)
    
    print_play("Please choose your next move and press 1 when you are ready to announce it.", lang)
    waitForConfirmationInput()
    
    legalMoves = getLegalMoves(board)
    
    while(True):
        move_str = audio_to_text(True, worB, lang)
        
        if (any(move_str in move for move in legalMoves)):
            user_move = ""
            for move in legalMoves:
                if move_str in move:
                    user_move = move
                    
            if (len(user_move) == 5):
                if (lang == 'en'):
                    print("You want to make promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("You want to make promotion at {}. Is this correct?".format(move_str[2:4]), lang)
                if (lang == 'es'):
                    print("You want to make promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("Quiere hacer la coronación en {}. ¿Es esto correcto?".format(move_str[2:4]), lang)
                if (lang == 'fr'):
                    print("You want to make promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("Vous voulez faire de la promotion en {}. Est-ce correct?".format(move_str[2:4]), lang)
                if (lang == 'de'):
                    print("You want to make promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("Möchten Sie eine Umwandlung auf {} machen?".format(move_str[2:4]), lang)
                if (lang == 'zh-cn'):
                    print("You want to make promotion at {}. Is this correct?".format(move_str[2:4]))
                    text_to_speech("您是否想升变{}?".format(move_str[2:4]), lang)
                    
                text = audio_to_text(False, worB, lang)[0]
            if (move_str == 'e1g1' or move_str == 'e8g8'):
                print_play("You want to make kingside castling. Is this correct?", lang)
                text = audio_to_text(False, worB, lang)[0]
            elif (move_str == 'e1c1' or move_str == 'e8c8'):
                print_play("You want to make queenside castling. Is this correct?", lang)
                text = audio_to_text(False, worB, lang)[0]
            else:
                if (lang == 'en'):
                    text_to_speech("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]), lang)
                    print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
                if (lang == 'es'):
                    text_to_speech("He detectado {} a {}. ¿Es esto correcto?".format(move_str[0:2], move_str[2:4]), lang)
                    print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
                if (lang == 'fr'):
                    text_to_speech("J'ai détecté {} à {}. Est-ce correct?".format(move_str[0:2], move_str[2:4]), lang)
                    print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
                if (lang == 'de'):
                    text_to_speech("Ich habe {} zu {} erkannt. Ist das richtig?".format(move_str[0:2], move_str[2:4]), lang)
                    print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
                if (lang == 'zh-cn'):
                    text_to_speech("您是从{}移动到{}了吗？".format(move_str[0:2], move_str[2:4]), lang)
                    print("I detected {} to {}. Is this correct?".format(move_str[0:2], move_str[2:4]))
                    
                text = audio_to_text(False, worB, lang)[0]
            if (text == 'n'):
                print_play("Please press 1 again when you are ready to announce your move.", lang)
                waitForConfirmationInput()
            else:
                fen_parts = board.fen().split(" ")
                move = chess.Move.from_uci(move_str)
                board.push(move)
                
                computerSide.userTurn(move)
                fen = convertToFenWithSpaces(fen_parts[0])
                print(fen)
                enpassant = fen_parts[3]
                plan(str(move), lang, worB, fen, enpassant)
                
                if (len(user_move) == 5):
                    print_play("You can only make queen promotion. Please place the queen on the desired square and press yes when you are done.", lang)
                    waitForConfirmationInput()
                
                # Store the move
                storeMovesList.add(move_str)
                storeMovesList.save()
                
                return True
        else:
            if (lang == 'en'):
                text_to_speech("I detected {} to {}. This is an illegal move. Please press yes again, when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]), lang)
                print("I detected {} to {}. This is an illegal move. Please press 1 again when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            if (lang == 'es'):
                text_to_speech("He detectado {} a {}. Este es un movimiento ilegal. Por favor, vuelva a presionar sí cuando esté listo para anunciar su movimiento.".format(move_str[0:2], move_str[2:4]), lang)
                print("I detected {} to {}. This is an illegal move. Please press 1 again when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            if (lang == 'fr'):
                text_to_speech("J'ai détecté {} à {}. Ceci est un coup illégal. Veuillez appuyer à nouveau sur oui, lorsque vous êtes prêt à annoncer votre coup.".format(move_str[0:2], move_str[2:4]), lang)
                print("I detected {} to {}. This is an illegal move. Please press 1 again when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            if (lang == 'de'):
                text_to_speech("Ich habe {} zu {} erkannt. Dies ist ein illegaler Schritt. Bitte drücken Sie erneut Ja, wenn Sie Ihren Schachzug ankündigen möchten.".format(move_str[0:2], move_str[2:4]), lang)
                print("I detected {} to {}. This is an illegal move. Please press 1 again when you are ready to announce your move.".format(move_str[0:2], move_str[2:4]))
            if (lang == 'zh-cn'):
                text_to_speech("您不能从{}移动到{}，这违反了规则。请重新思考并在落子后按下确认键。".format(move_str[0:2], move_str[2:4]), lang)
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
    
    if (choice == '.'):
        choice = 'n'
    else:
        choice = 'y'
    return choice

def waitForConfirmationInput():
    confirmed = getch.getch()
    if(confirmed == '\n'):
        return True
    elif(confirmed =='q'):
        sys.exit()
    else:
        return waitForConfirmationInput()
    
def audio_to_text(recogniseMove, worB, lang):
    text = "Sorry, can you please repeat that?"
    
    while (text == "Sorry, can you please repeat that?"):
        #Initalize microphone
        audio = pyaudio.PyAudio()
        
        dev_index = -1
        for ii in range(audio.get_device_count()):
            name = audio.get_device_info_by_index(ii).get('name')
            if (mic_name in name):
                dev_index = ii 
            
        if (dev_index == -1):
            play_sound('sounds/mic_not_detected.wav')
            print("Unable to detect microphone. Please unplug and plug it again.", lang)
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
        if (text == "Sorry, can you please repeat that?" and recogniseMove == False):
            print_play(text, lang)
            
        if (recogniseMove == True):
            words = text.split(" ")
            if not (len(words) == 4):
                text = "Sorry, can you please repeat that?"
                print_play(text, lang)
            else:
                if (words[1] == 'queenside'):
                    if (worB == 'w'):
                        text = 'e1c1'
                    else:
                        text = 'e8c8'
                else:
                    if (words[1] == 'kingside'):
                        if (worB == 'w'):
                            text = 'e1g1'
                        else:
                            text = 'e8g8'
                    else:
                        text = words[0] + words[2]
    return text
    

def gameplayloop(board, lang):
    worB = ""
    storeMovesList = storeMoves()
    print_play("Please confirm the board is clear before proceeding by pressing 1.", lang)
    waitForConfirmationInput()
    
    print_play("Please start the calibration process. Refer to the instruction manual for help.", lang)
    print('started request')
    try:
        requests.post("http://ev3:8000/init", "POST")
    except requests.exceptions.ConnectionError:
        print_play("EV3 is not connected.", lang)
        sys.exit()
    print('finished request')
    print_play("Calibration completed successfully.", lang)

    print_play("2.Select mode of play (e for easy, m for moderate, h for hard, p for pro):", lang)

    mode = audio_to_text(False, worB, lang)[0].lower()
    
    mode_text_dict_en = {
        "e":'easy',
        "m":'moderate',
        "h":'hard',
        "p":'pro'
    }
    
    mode_text_dict_es = {
        "e":'fácil',
        "m":'moderado',
        "h":'difícil',
        "p":'profesional'
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
        text_to_speech("Ha seleccionado el modo {}.".format(mode_text_dict_es.get(mode, 'easy')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))
    if (lang == 'fr'):
        text_to_speech("Vous avez sélectionné le mode {}.".format(mode_text_dict_fr.get(mode, 'facile')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))
    if (lang == 'de'):
        text_to_speech("Sie haben den {} ausgewählt.".format(mode_text_dict_de.get(mode, 'einfachen')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))
    if (lang == 'zh-cn'):
        text_to_speech("您选择了{} 模式。".format(mode_text_dict_zh_cn.get(mode, '简单')), lang)
        print("You have selected {} mode.".format(mode_text_dict_en.get(mode, 'easy')))

    print_play("2.White or black? w or b: ", lang)
    
    worB = audio_to_text(False, worB, lang)[0].lower()
    
    if not (worB == 'w' or worB == 'b'):
        worB == 'w'
    if (worB == 'w'):
        print_play("You have selected white.", lang)
        print_play("Please set up the board, placing the white pieces on your side. Confirm by pressing yes.", lang)
        waitForConfirmationInput()
        
    else:
        print_play("You have selected black.", lang)
        print_play("Please set up the board, placing the black pieces on your side. Confirm by pressing yes.", lang)
        waitForConfirmationInput()
        
    storeMovesList.add('user:' + worB)

    mode_dict = {
        "e":1,
        "m":3,
        "h":5,
        "p":7
    }

    depth = mode_dict.get(mode, 1)
    computerSide = ChessMatch(float(depth)) #set up our AI interface, initialised with a time it may process the board for

    prom_dict_en = {
        "q":"queen",
        "n":"knight",
        "r":"rook",
        "b":"bishop"
    }
    
    prom_dict_es = {
        "q":"reina",
        "n":"caballo",
        "r":"torre",
        "b":"alfil"
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
                if (len(str(x)) == 5):
                    if (lang == 'en'):
                        text_to_speech("Promotion! Please place the queen on {} and press yes when you are ready.".format(move[2:4]), lang)
                    if (lang == 'es'):
                        text_to_speech("¡Promoción! Coloque la reina en {} y oprima sí cuando esté listo.".format(move[2:4]), lang)
                    if (lang == 'fr'):
                        text_to_speech("Promotion! Placez la reine sur {} et appuyez sur Oui lorsque vous êtes prêt.".format(move[2:4]), lang)
                    if (lang == 'de'):
                        text_to_speech("Beförderung! Bitte platzieren Sie die Dame auf {} und drücken Sie Ja, wenn Sie fertig sind.".format(move[2:4]), lang)
                    if (lang == 'zh-cn'):
                        text_to_speech("升变！请将皇后放置到{}并按确认键。".format(move[2:4]), lang)
                    
                    waitForConfirmationInput()
                    
                fen = convertToFenWithSpaces(fen_parts[0])
                enpassant = fen_parts[3]
                
                # Store move
                storeMovesList.add(str(x))
                storeMovesList.save()
                
                if(not str(x)[-1].isdigit()):
                    x = str(x)[0:4]
                    
                plan(str(x), lang, worB, fen, enpassant)
                
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
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("Hice la promoción de la {}. ¡Su turno!".format(prom_dict_es.get(piece)), lang)
                    if (lang == 'fr'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("J'ai fait la promotion de la {}. À votre tour!".format(prom_dict_fr.get(piece)), lang)
                    if (lang == 'de'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("Ich habe eine Umwandlung auf {} gemacht. Du bist dran!".format(prom_dict_de.get(piece)), lang)
                    if (lang == 'zh-cn'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("我升变了{},到你了!".format(prom_dict_zh_cn.get(piece)), lang)
                    
                else:
                    if (lang == 'en'):
                        text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'es'):
                        text_to_speech("He movido {} a {}. ¡Su turno!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
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
                stopNow = userTurn(board, computerSide, worB, lang, storeMovesList)
                print(board)
                if(not stopNow):
                    computerSide.endgame()
                    break
    else:
        while (True):
            stopNow = userTurn(board, computerSide, worB, lang, storeMovesList)
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
                
                fen = convertToFenWithSpaces(fen_parts[0])
                enpassant = fen_parts[3]
                
                if(not str(x)[-1].isdigit()):
                    x = str(x)[0:4]
                    
                plan(str(x), lang, worB, fen, enpassant)
                
                board.push(x)
                if (len(str(x)) == 5):
                    if (lang == 'en'):
                        text_to_speech("Promotion! Please place the queen on {} and press yes when you are ready.".format(move[2:4]), lang)
                    if (lang == 'es'):
                        text_to_speech("¡Promoción! Coloque la reina en {} y oprima sí cuando esté listo.".format(move[2:4]), lang)
                    if (lang == 'fr'):
                        text_to_speech("Promotion! Placez la reine sur {} et appuyez sur Oui lorsque vous êtes prêt.".format(move[2:4]), lang)
                    if (lang == 'de'):
                        text_to_speech("Beförderung! Bitte platzieren Sie die Dame auf {} und drücken Sie Ja, wenn Sie fertig sind.".format(move[2:4]), lang)
                    if (lang == 'zh-cn'):
                        text_to_speech("升变！请将皇后放置到{}并按确认键。".format(move[2:4]), lang)
                        
                    waitForConfirmationInput()
                
                # Store move 
                storeMovesList.add(str(x))
                storeMovesList.save()
                
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
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("Hice la promoción de la {}. ¡Su turno!".format(prom_dict_en.get(piece)), lang)
                    if (lang == 'fr'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("J'ai fait la promotion de la {}. À votre tour!".format(prom_dict_fr.get(piece)), lang)
                    if (lang == 'de'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("Ich habe eine Umwandlung auf {} gemacht. Du bist dran!".format(prom_dict_de.get(piece)), lang)
                    if (lang == 'zh-cn'):
                        print("I made {} promotion. Your turn!".format(prom_dict_en.get(piece)))
                        text_to_speech("我升变了{},到你了!".format(prom_dict_zh_cn.get(piece)), lang)
                    
                else:
                    if (lang == 'en'):
                        text_to_speech("I moved from {} to {}. Your turn!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
                    if (lang == 'es'):
                        text_to_speech("He movido {} a {}. ¡Su turno!".format(str(x)[0:2], str(x)[2:4]), lang)
                        print("AI makes move: {}.".format(x),"\n")
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

def main(lang):
    board = chess.Board()
    
    gameplayloop(board, lang)

if __name__ == '__main__':
    main()
