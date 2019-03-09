import numpy as np
import os
from PIL import Image

app_root = os.path.dirname(os.path.abspath(__file__))

def detect_empty(model, previousFEN):
    # Read rows from the FEN notation of the previous board state
    fen_notation = previousFEN
    r8, r7, r6, r5, r4, r3, r2, last = fen_notation.split('/')
    r1 = last.split(' ')[0]
    additional_notation = last.split(' ')[1] + ' ' + last.split(' ')[2] + ' ' + last.split(' ')[3] + ' ' + last.split(' ')[4] + ' ' + last.split(' ')[5]

    row_num = 8
    image_names = []
    row_list = [r8, r7, r6, r5, r4, r3, r2, r1]

    # Find all white pieces in the previous board state
    for row in row_list:
        indices_uppercase = [i for i, c in enumerate(row) if c.isupper()]
        letters = [chr(num + ord('a')) for num in indices_uppercase]
        if len(letters) != 0:
            positions = [letter + str(row_num) for letter in letters]
            for p in positions:
                image_names.append(p + '.jpg')
        row_num = row_num - 1

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

    # Find the image (previously containing a white piece) with highest probability of being empty after the user's move
    max_indices = predictions.argmax(axis=0)
    max_index_black = max_indices[2]
    max_index_wooden = max_indices[5]
    if predictions[max_index_black][2] >= predictions[max_index_wooden][5]:
        max_index = max_index_black
    else:
        max_index = max_index_wooden

    empty_position = image_names[max_index][0:2]
    row = row_list[len(row_list) - int(empty_position[1])]
    column = ord(empty_position[0]) - ord('a')
    piece = row[column]
    row = list(row)
    row[column] = '*'
    row = ''.join(row)
    row_list[len(row_list) - int(empty_position[1])] = row

    # Create a new FEN notation changing the origin square to empty
    new_fen = ''
    for row in row_list:
        new_fen = new_fen + row + '/'
    new_fen = new_fen[:-1] + ' ' + additional_notation
    return (empty_position, piece, new_fen)
