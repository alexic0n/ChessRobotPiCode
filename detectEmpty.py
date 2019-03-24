import numpy as np
import os
from PIL import Image

app_root = os.path.dirname(os.path.abspath(__file__))

def detect_empty(model, previousFEN, valid_origins, probability_rank, WorB):
    # Read rows from the FEN notation of the previous board state
    fen_notation = ''
    for ch in previousFEN:
        if ch.isdigit():
            fen_notation = fen_notation + '*' * (ord(ch) - ord('0'))
        else:
            fen_notation = fen_notation + ch

    r8, r7, r6, r5, r4, r3, r2, last = fen_notation.split('/')
    r1 = last.split(' ')[0]
    row_num = 8
    image_names = []
    row_list = [r8, r7, r6, r5, r4, r3, r2, r1]

    # Create a list with vaild origin image names
    image_names = []
    for square in valid_origins:
        image_names.append(square + '.jpg')

    # Crop pixels off the sides of the square (to avoid parts of other squares present in the image)
    pixels = 224
    new_pixels = 215
    left = (pixels - new_pixels) / 2
    top = (pixels - new_pixels) / 2
    right = (pixels + new_pixels) / 2
    bottom = (pixels + new_pixels) / 2

    # Add the detected white pieces in the previous board state to the testing data
    data = []

    for image_name in image_names:
        image = Image.open(os.path.join(app_root,'images', 'Cropped', '{}').format(image_name))
        image = image.crop((left, top, right, bottom))
        image = image.resize((pixels, pixels), Image.ANTIALIAS)
        image = np.array(image)
        data.append(image)
    data = np.array(data)
    
    # Generate a list of predictions for the testing data
    predictions = model.predict(data)

    while probability_rank>=0:
        # Find the image (previously containing a white piece) with highest probability of being empty after the user's move
        max_indices = predictions.argmax(axis=0)
        max_index_black = max_indices[2]
        max_index_wooden = max_indices[5]
        if predictions[max_index_black][2] >= predictions[max_index_wooden][5]:
            max_index = max_index_black
        else:
            max_index = max_index_wooden
        predictions[max_index_black][2] = -1
        predictions[max_index_wooden][5] = -1
        probability_rank = probability_rank - 1

    empty_position = image_names[max_index][0:2]
    row = row_list[len(row_list) - int(empty_position[1])]
    column = ord(empty_position[0]) - ord('a')
    piece = row[column]

    return (empty_position, piece)
