import numpy as np
from PIL import Image
import os

app_root = os.path.dirname(os.path.abspath(__file__))

def detect_move(model, piece, validmoves, WorB, kingside, queenside):
    # Crop pixels off the sides of the square (to avoid parts of other squares present in the image)
    pixels = 224
    new_pixels = 215
    left = (pixels - new_pixels) / 2
    top = (pixels - new_pixels) / 2
    right = (pixels + new_pixels) / 2
    bottom = (pixels + new_pixels) / 2
    
    # List of possible moves(i.e. destination squares) for the given piece
    image_names = validmoves
    
    # Add the possible destination squares to the testing data
    data = []
    data_white_kingside = []
    data_white_queenside = []
    data_black_kingside = []
    data_black_queenside = []

    for image_name in image_names:
        image = Image.open(os.path.join(app_root, 'images', 'Cropped', ('{}.jpg').format(image_name)))
        image = image.crop((left, top, right, bottom))
        image = image.resize((pixels, pixels), Image.ANTIALIAS)
        image = np.array(image)
        data.append(image)

    castling_image_names = ["f1.jpg", "g1.jpg", "c1.jpg", "d1.jpg", "f8.jpg", "g8.jpg", "c8.jpg", "d8.jpg"]
    for image_name in castling_image_names:
        image = Image.open(os.path.join(app_root, 'images', 'Cropped', image_name))
        image = image.crop((left, top, right, bottom))
        image = image.resize((pixels, pixels), Image.ANTIALIAS)
        image = np.array(image)

        if (image_name == "f1.jpg" or image_name == "g1.jpg"):
            data_white_kingside.append(image) 
        if (image_name == "c1.jpg" or image_name == "d1.jpg"):
            data_white_queenside.append(image) 
        if (image_name == "f8.jpg" or image_name == "g8.jpg"):
            data_black_kingside.append(image) 
        if (image_name == "c8.jpg" or image_name == "d8.jpg"):
            data_black_queenside.append(image) 
            
    data = np.array(data)
    data_white_kingside = np.array(data_white_kingside)
    data_white_queenside = np.array(data_white_queenside)
    data_black_kingside = np.array(data_black_kingside)
    data_black_queenside = np.array(data_black_queenside)

    threshold = 0.5
    if WorB == 'w':
        first = 0
        second = 3

        # Check if castling move has been made
        if (kingside):
            castling_predictions = model.predict(data_white_kingside)
            if (castling_predictions[0][first] > threshold or castling_predictions[0][second] > threshold) and (castling_predictions[1][first] > threshold or castling_predictions[$
               return "f1g1"
        if (queenside):
            castling_predictions = model.predict(data_white_queenside)
            if (castling_predictions[0][first] > threshold or castling_predictions[0][second] > threshold) and (castling_predictions[1][first] > threshold or castling_predictions[$
               return "c1d1"
    else:
        first = 1
        second = 4

        # Check if castling move has been made
        if (kingside):
            castling_predictions = model.predict(data_black_kingside)
            if (castling_predictions[0][first] > threshold or castling_predictions[0][second] > threshold) and (castling_predictions[1][first] > threshold or castling_predictions[$
               return "f8g8"
        if (queenside):
            castling_predictions = model.predict(data_black_queenside)
            if (castling_predictions[0][first] > threshold or castling_predictions[0][second] > threshold) and (castling_predictions[1][first] > threshold or castling_predictions[$
               return "c8d8"
   
    # Generate a list of predictions for the testing data
    predictions = model.predict(data) 

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

