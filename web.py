from flask import Flask, request, abort, Markup
import markdown
import uuid
import os
import bjoern
import json
import speech_recognition as sr

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

@app.route('/speech_recognition', methods=['POST'])
def speech_recognition():
    if not (request.files['user_speech']):
        abort('401')
    storage_path = os.path.join(app_root)
    audio_path = os.path.join(storage_path, 'audio.wav')
    request.files['user_speech'].save(audio_path)

    with open ('Checkmate.json', 'r') as file:
        credential = file.read ()

    r = sr.Recognizer()

    with sr.AudioFile("audio.wav") as source:
        audio = r.record(source)

    text = r.recognize_google_cloud (audio, language = "en-us", credentials_json = credential, preferred_phrases = ['yes', 'no', 'black', 'white', 'easy', 'moderate', 'hard', 'pro'])
    print ("Google Cloud Speech Recognition thinks you said: " + text)

    res = json.dumps({'text':text})

    return res

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

