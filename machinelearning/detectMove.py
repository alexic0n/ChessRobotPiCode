import numpy as np
from PIL import Image
import os

app_root = os.path.dirname(os.path.abspath(__file__))

def detect_move(model, piece, validmoves, WorB):
    # Crop pixels off the sides of the square (to avoid parts of other squares present in the image)
    pixels = 224
    new_pixels = 215
    left = (pixels - new_pixels) / 2
    top = (pixels - new_pixels) / 2
    right = (pixels + new_pixels) / 2
    bottom = (pixels + new_pixels) / 2

    # List of possible moves(i.e. destination squares) for the given piece
    #validmoves = validmoves.replace('[', '')
    #validmoves = validmoves.replace(']', '')
    #validmoves = validmoves.replace('\'', '')
    #image_names = validmoves.split(', ')
    image_names = validmoves

    # Add the possible destination squares to the testing data
    data = []
    for image_name in image_names:
        print(image_name)
        image = Image.open(os.path.join(app_root, 'images', 'Cropped', ('{}.jpg').format(image_name)))
        image = image.crop((left, top, right, bottom))
        image = image.resize((pixels, pixels), Image.ANTIALIAS)
        image = np.array(image)
        data.append(image)
    data = np.array(data)

    # Generate a list of predictions for the testing data
    predictions = model.predict(data)

    if WorB == 'w':
        first = 0
        second = 3
    else:
        first = 1
        second = 4
    # Find the destination square with highest probability of containing a white piece after the user's move
    max_indices = predictions.argmax(axis=0)
    max_index_black = max_indices[first]
    max_index_wooden = max_indices[second]
    if predictions[max_index_black][first] >= predictions[max_index_wooden][second]:
        max_index = max_index_black
    else:
        max_index = max_index_wooden
    piece_position = image_names[max_index][0:2]

    return piece_position
