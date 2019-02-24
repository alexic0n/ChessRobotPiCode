import numpy as np
from PIL import Image

def detect_move(model, piece, new_fen):
    # Read rows from the FEN notation of the previous board state
    r8, r7, r6, r5, r4, r3, r2, last = new_fen.split('/')
    r1 = last.split(' ')[0]
    additional_notation = last.split(' ')[1] + ' ' + last.split(' ')[2] + ' ' + last.split(' ')[3] + ' ' + \
                          last.split(' ')[4] + ' ' + last.split(' ')[5]
    row_list = [r8, r7, r6, r5, r4, r3, r2, r1]

    # Crop pixels off the sides of the square (to avoid parts of other squares present in the image)
    pixels = 224
    new_pixels = 215
    left = (pixels - new_pixels) / 2
    top = (pixels - new_pixels) / 2
    right = (pixels + new_pixels) / 2
    bottom = (pixels + new_pixels) / 2

    # List of possible moves(i.e. destination squares) for the given piece
    # HARDCODED (will later use AI's functionality of predicting the possible moves for a given piece)
    image_names = ['b5.jpg', 'a6.jpg', 'b3.jpg', 'a2.jpg', 'd4.jpg', 'd3.jpg', 'e2.jpg', 'f1.jpg']

    # Add the possible destination squares to the testing data
    data = []
    for image_name in image_names:
        image = Image.open(('Logitech Webcam/Cropped/{}').format(image_name))
        image = image.crop((left, top, right, bottom))
        image = image.resize((pixels, pixels), Image.ANTIALIAS)
        image = np.array(image)
        data.append(image)
    data = np.array(data)

    # Generate a list of predictions for the testing data
    predictions = model.predict(data)

    # Find the destination square with highest probability of containing a white piece after the user's move
    max_indices = predictions.argmax(axis=0)
    max_index_black = max_indices[0]
    max_index_wooden = max_indices[3]
    if predictions[max_index_black][0] >= predictions[max_index_wooden][3]:
        max_index = max_index_black
    else:
        max_index = max_index_wooden
    piece_position = image_names[max_index][0:2]
    row_str = row_list[len(row_list) - int(piece_position[1])]
    column = ord(piece_position[0]) - ord('a')

    new_row = ''
    for ch in row_str:
        if ch.isdigit():
            new_row = new_row + '*' * int(ch)
        else:
            new_row = new_row + ch
    new_row = list(new_row)
    new_row[column] = piece
    new_row = ''.join(new_row)
    row_list[len(row_list) - int(piece_position[1])] = new_row

    # Create a new FEN notation changing the origin square to empty
    new_fen = ''
    for row in row_list:
        new_fen = new_fen + row + '/'
    new_fen = new_fen[:-1] + ' ' + additional_notation

    # Save the new FEN notation into the .txt file
    with open("Board state/previousFEN.txt", "w") as text_file:
        print(new_fen, file=text_file)
    return piece_position

