from flask import Flask, request, abort, Markup
import markdown
import uuid
import os
import bjoern
import json

# ML classes
import cv2
import glob
from BoardDetection import segmentation_board as find_corners
from Crop import crop_squares
from Initialize import load_weights
from Initialize import initialize_fen
from detectEmpty import detect_empty
from detectMove import detect_move
from model import model

# Flask instances are callable WSGI apps, initialise the app
app = Flask(__name__)
app_root = os.path.dirname(os.path.abspath(__file__))


# define your routes
@app.route('/')
def index():
    with open(os.path.join(app_root, 'README.md')) as r:
        return Markup(markdown.markdown(r.read()))

@app.route('/pieces', methods=['POST'])
def pieces():
    name = 'image.jpg'

    storage_path = os.path.join(app_root, 'images')

    image_path = os.path.join(storage_path, name)

    if not (request.files['board'] and request.files['fen'] and request.files['validmoves'] and request.files['userResponse'] and request.files['userResponseCastling'] and request$
        abort('401')
    request.files['board'].save(image_path)

    WorB = request.files['WorB'].read().decode()
    userResponse = request.files['userResponse'].read().decode()
    userResponseCastling = request.files['userResponseCastling'].read().decode()
    probability_rank = request.files['probability_rank'].read().decode()
    fen = request.files['fen'].read().decode()

    kingside = False
    queenside = False

    # Controls all other functions
    # Take last image from the webcam
    image = cv2.imread(image_path)

    # Crop the board into 64 squares
    crop_squares(image_path)

    if userResponseCastling == 'false':
        # Check if castling move is available
        castling = fen.split(" ")[2]
        if (WorB == 'w'):
            lastRow = fen.split(" ")[0].split("/")[7]
            if "K" in castling:
                if lastRow[-2] == "2":
                    kingside = True
            if "Q" in castling:
                if lastRow[1] == "3":
                    queenside = True
        else:
            firstRow = fen.split(" ")[0].split("/")[0]
            if "k" in castling:
                if firstRow[-2] == "2":
                    kingside = True
            if "q" in castling:
                if firstRow[1] == "3": 
                    queenside = True
            
    # Move detection
    ## Detect the most probable origin square
    (empty_square, piece) = detect_empty(model, fen, userResponse, int(probability_rank), WorB, kingside, queenside)

    if (len(empty_square) == 4):
        if (empty_square == "e1h1") or (empty_square == "e8h8"):
            kingside = True
        else: 
            kingside = False

        if (empty_square == "e1a1") or (empty_square == "e8a8"):
            queenside = True
        else:
            queenside = False
    else:
        kingside = False
        queenside = False 
            
    ## Detect the most probable destination square
    moves = request.files['validmoves'].read().decode()

    moves = moves.replace('[', '')
    moves = moves.replace(']', '')
    moves = moves.replace('\'', '')
    valid_moves = moves.split(', ')
    valid_moves = [move[2:4] for move in valid_moves if move[0:2] == empty_square]
    
    if valid_moves == [] and not(kingside == True or queenside == True):
        userResponse = 'true'
        r = json.dumps({'move':'-1', 'status':'-1', 'userResponse':userResponse, 'probability_rank':probability_rank})
        return r

    (piece_position) = detect_move(model, piece, valid_moves, WorB, kingside, queenside)

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
 
    r = json.dumps({'move':move, 'status':response, 'userResponse':'false', 'probability_rank':probability_rank})
    
    return r
 
if __name__ == '__main__':
    #bjoern.run(app, '0.0.0.0', 8000)
    app.run(host='0.0.0.0', port=8000)


