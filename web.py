
from pydub import AudioSegment
from flask import Flask, request, abort, Markup, send_file
import markdown
import uuid
import os
import bjoern
import json
import speech_recognition as sr
from gtts import gTTS
import wave

# ML classes
import cv2
import numpy as np
import glob
from BoardDetection import segmentation_board as find_corners
from Crop import crop_squares
from Initialize import load_weights
from Initialize import initialize_fen
from detectEmpty import detect_empty
from detectMove import detect_move
from model import model
from PIL import Image

# Flask instances are callable WSGI apps, initialise the app
app = Flask(__name__)
app_root = os.path.dirname(os.path.abspath(__file__))


# define your routes
@app.route('/')
def index():
    with open(os.path.join(app_root, 'README.md')) as r:
        return Markup(markdown.markdown(r.read()))

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    if not (request.files['text'] and request.files['lang']):
        abort('401')
    
    text = request.files['text'].read().decode()
    lang = request.files['lang'].read().decode()
    speech = gTTS(text=text, lang=lang)
    speech.save('text_to_speech.mp3')

    speech = AudioSegment.from_mp3('text_to_speech.mp3')
    speech.export('text_to_speech.wav', format="wav")

    return send_file(
         'text_to_speech.wav', 
         mimetype="audio/wav", 
         as_attachment=True, 
         attachment_filename="text_to_speech.wav")

@app.route('/speech_recognition', methods=['POST'])
def speech_recognition():
    if not (request.files['user_speech'] and request.files['lang']):
        abort('401')
    storage_path = os.path.join(app_root)
    audio_path = os.path.join(storage_path, 'audio.wav')
    request.files['user_speech'].save(audio_path)

    lang_code = request.files['lang'].read().decode()

    lang_dict = {
        'en':'en-GB',
        'es':'es-ES',
        'fr':'fr-FR',
        'de':'de-DE',
        'zh-cn':'zh'
    }

    lang = lang_dict.get(lang_code, 'en-GB')

    with open ('Checkmate.json', 'r') as file:
        credential = file.read ()

    r = sr.Recognizer()

    with sr.AudioFile("audio.wav") as source:
        audio = r.record(source)
    expected_words_en = ['one', 'two', 'three', 'four' ,'yes', 'no', 'black', 'white', 'easy', 'moderate', 'hard', 'pro', 'to', 'make', 'kingside', 'queenside', 'castling', 'yeah', 'yep', 'nope', 'wide', 'heart', 'heard']
    expected_words_es = ['uno', 'dos', 'tres', 'cuatro', 'sí', 'no', 'negro', 'blanco', 'fácil', 'moderado', 'difícil', 'profesional', 'a', 'haga', 'corto', 'largo', 'enroque']
    expected_words_fr = ['un', 'deux', 'trois', 'quatre', 'oui', 'non', 'noir', 'blanc', 'facile', 'modéré', 'difficile', 'pro', 'à', 'fais', 'petit', 'grand', 'roque']
    expected_words_de = ['eins', 'zwei', 'drei', 'vier', 'ja', 'nein', 'schwarz', 'weiss', 'einfachen', 'mittleren', 'harten', 'Pro-Modus', 'nach', 'mache', 'kurze', 'lange', 'Rochade' ]
    expected_words_zh_cn = ['一', '二', '三', '四', '是', '否', '黑', '白', '简单', '中等', '困难', '专家', '移动到', '进行', '王翼易位', '后翼易位', '后1亿位', '王1亿位' ]

    squares = []
    for letter in "abcdefgh":
        for num in "12345678":
            square = letter + num
            squares.append(square)
        if (lang_code == 'zh-cn'):
            for num in "一二三四五六七八":
                square = letter + num
                squares.append(square)

    if(lang_code == 'en'):
        expected_words = expected_words_en
    if(lang_code == 'es'):
        expected_words = expected_words_es
    if(lang_code == 'fr'):
        expected_words = expected_words_fr
    if(lang_code == 'de'):
        expected_words = expected_words_de
    if(lang_code == 'zh-cn'):
        expected_words = expected_words_zh_cn

    try:
        text = r.recognize_google_cloud (audio, language = lang, credentials_json = credential, preferred_phrases = expected_words+squares).lower()
        print(text)
        words = text.split(" ")
        print(words)
        if(lang_code == 'en'):
            if('castling' in words):
                if ('queenside' in words):
                    return json.dumps({'text':'make queenside castling '})
                if('kingside' in words):
                    return json.dumps({'text':'make kingside castling '})
        if(lang_code == 'es'):
            if('enroque' in words):
                if ('largo' in words):
                    return json.dumps({'text':'make queenside castling '})
                if('corto' in words):
                    return json.dumps({'text':'make kingside castling '})
        if(lang_code == 'fr'):
            if('roque' in words):
                if ('grand' in words):
                    return json.dumps({'text':'make queenside castling '})
                if('petit' in words):
                    return json.dumps({'text':'make kingside castling '})
        if(lang_code == 'de'):
            if('rochade' in words):
                if ('lange' in words):
                    return json.dumps({'text':'make queenside castling '})
                if('kurze' in words):
                    return json.dumps({'text':'make kingside castling '})
        if(lang_code == 'zh-cn'):
            if('后翼易位' in text or '后1亿位' in text):
                return json.dumps({'text':'make queenside castling '})
            if ('王翼易位' in text or '王1亿位' in text):
                return json.dumps({'text':'make kingside castling '})

        if (lang_code == 'zh-cn'):
            square_origin = " "
            square_dest = " "

            ind = 0
            while (ind<len(text)-1):
                letter = text[ind]
                if (letter == '1'):
                    letter = 'e'
                digit = text[ind+1]

                if(digit == '一'):
                    digit = '1'
                if(digit == '二'):
                    digit = '2'
                if(digit == '三'):
                    digit = '3'
                if(digit == '四'):
                    digit = '4'
                if(digit == '五'):
                    digit = '5'
                if(digit == '六'):
                    digit = '6'
               if(digit == '七'):
                    digit = '7'
                if(digit == '八' or digit == '吧'):
                    digit = '8'

                if ((letter + digit) in squares):
                    if (square_origin == " "):
                        square_origin = letter + digit
                    else: 
                        square_dest = letter + digit
                        break
                ind = ind + 1

            if (not square_origin == " " and not square_dest == " "):
                print('Test')
                return json.dumps({'text':square_origin + " to " + square_dest + " "})

        #if (not lang_code == 'zh-cn' and len(words) >= 4 and words[0] in squares and words[2] in squares):
        #    return json.dumps({'text':words[0] + " to " + words[2] + " "})
        else: 
            square_origin = " "
            square_dest = " "

            ind = 0
            while (ind<len(text)-1):
                letter = text[ind]
                digit = text[ind+1]

                if ((letter + digit) in squares):
                    if (square_origin == " "):
                        square_origin = letter + digit
                    else: 
                        square_dest = letter + digit
                        break
                ind = ind + 1

            if (not square_origin == " " and not square_dest == " "):
                print('Test')
                return json.dumps({'text':square_origin + " to " + square_dest + " "})


        word_index = 0
        for word in (expected_words):
             if (word in text):
                 print ("Google Cloud Speech Recognition thinks you said: " + word)
                 return json.dumps({'text':expected_words_en[word_index]})
             word_index = word_index + 1
        return json.dumps({'text':"Sorry, can you please repeat that?"})
    except sr.UnknownValueError:
        return json.dumps({'text':"Sorry, can you please repeat that?"})
    except sr.RequestError:
        return json.dumps({'text': "Sorry, I could not request results from Google Speech Recognition Service. Please try again later or use keyboard control instead."})

@app.route('/pieces', methods=['POST'])
def pieces():
    name = 'image.jpg'

    storage_path = os.path.join(app_root, 'images')
    image_path = os.path.join(storage_path, name)

    if not (request.files['board'] and request.files['fen'] and request.files['validmoves']  and request.files['kingside'] and request.files['queenside'] and request.files['probability_rank'] and request.files[$
        abort('401')
    request.files['board'].save(image_path)

    WorB = request.files['WorB'].read().decode()
    kingside = request.files['kingside'].read().decode()
    queenside = request.files['queenside'].read().decode()
    probability_rank = request.files['probability_rank'].read().decode()
    fen = request.files['fen'].read().decode()
    moves = request.files['validmoves'].read().decode()
    rotateImage = request.files['rotateImage'].read().decode()

    if (request.files['firstImage'].read().decode() == 'true'):
        # Take last image from the webcam
        image = cv2.imread(image_path)

        # Crop the board into 64 squares
        crop_squares(image_path)

        # Crop pixels off the sides of the square (to avoid parts of other squares present in the image)
        pixels = 224
        new_pixels = 215
        left = (pixels - new_pixels) / 2
        top = (pixels - new_pixels) / 2
        right = (pixels + new_pixels) / 2
        bottom = (pixels + new_pixels) / 2
  
        data = []

        for image_name in ['a1', 'h8']:
            image = Image.open(os.path.join(app_root, 'images', 'Cropped', ('{}.jpg').format(image_name)))
            image = image.crop((left, top, right, bottom))
            image = image.resize((pixels, pixels), Image.ANTIALIAS)
            image = np.array(image)
            data.append(image)
        data = np.array(data)

        predictions = model.predict(data)

        # Probabilities of a1 and h8 containing white or black piece
        a1_white = max(predictions[0][0], predictions[0][3]) 
        a1_black = max(predictions[0][1], predictions[0][4])
        h8_white = max(predictions[1][0], predictions[1][3])
        h8_black = max(predictions[1][1], predictions[1][4])

        if (a1_black * h8_white > a1_white * h8_black):
            rotateImage = 'true'

    # Controls all other functions
    # Take last image from the webcam
    image = cv2.imread(image_path)

    # Rotate image if necessary
    if (rotateImage == 'true'):
         (h, w) = image.shape[:2]
         # Calculate the center of the image
         center = (w / 2, h / 2)

         M = cv2.getRotationMatrix2D(center, 180, 1.0)
         image = cv2.warpAffine(image, M, (w, h))  

         # Save the rotated image
         cv2.imwrite(image_path, image)

    # Crop the board into 64 squares
    crop_squares(image_path)

    # Move detection
    ## Detect the most probable origin square
    moves = moves.replace('[', '')
    moves = moves.replace(']', '')
    moves = moves.replace('\'', '')
    valid_moves = moves.split(', ')
    valid_origins = [move[0:2] for move in valid_moves]

    (empty_square, piece) = detect_empty(model, fen, valid_origins, int(probability_rank), WorB)

    ## Detect the most probable destination square
    valid_destinations = [move[2:4] for move in valid_moves if move[0:2] == empty_square]

    (piece_position) = detect_move(model, piece, valid_destinations, WorB, kingside, queenside)

    if (len(piece_position) == 3):
        empty_square = 'e' + empty_square[1:]

    move = empty_square + piece_position
    
    for legal_move in valid_moves:
        if (move in legal_move and len(legal_move) == 5):
            move = move + 'q'

    piece_dict = {
        "p":"Pawn",
        "b":"Bishop",
        "n":"Knight",
        "q":"Queen",
        "r":"Rook",
        "k":"King"
    }

    response = '{} moved from {} to {}'.format(piece_dict.get(piece.lower()), empty_square, piece_position)
    
    print(response)
 
    r = json.dumps({'move':move, 'status':response, 'probability_rank':probability_rank, 'rotateImage': rotateImage})
    
    return r
 
if __name__ == '__main__':
    #bjoern.run(app, '0.0.0.0', 8000)
    app.run(host='0.0.0.0', port=8000)
