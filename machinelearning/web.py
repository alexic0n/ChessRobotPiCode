from flask import Flask, request, abort, Markup
import markdown
import uuid
import os
import bjoern

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
    name = '{uuid}.jpg'.format(uuid=uuid.uuid4())

    storage_path = os.path.join(app_root, 'images')

    image_path = os.path.join(storage_path, name)

    if not (request.files['board'] and request.form['fen'] and request.form['validmoves']):
        abort('401')
    
    request.files['board'].save(image_path)
    
    # Controls all other functions
    # Take last image from the webcam
    image = cv2.imread(image_path)

    # Board segmentation
    (list1, list2) = find_corners(image)
    image = image[list1[1]:list2[1], list1[0]:list2[0]]
    cv2.imwrite(image_path, image)

    # Crop the board into 64 squares
    crop_squares(image_path)

    # Move detection
    ## Detect the most probable origin square
    (empty_square, piece, new_fen) = detect_empty(model, request.form['fen'])
    ## Detect the most probable destination square
    (piece_position, new_fen) = detect_move(model, piece, new_fen, request.form['validmoves'])
    
    response = '{} moved from {} to {}\n{}'.format(piece, empty_square, piece_position, new_fen)
    
    print(response)
    
    return response
 
if __name__ == '__main__':
    bjoern.run(app, '0.0.0.0', 8000)
    print("App running on port 8000")
