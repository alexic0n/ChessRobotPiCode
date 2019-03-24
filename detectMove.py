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

    castling_image_names = ["g1.jpg", "c1.jpg","g8.jpg", "c8.jpg"]
    for image_name in castling_image_names:
        image = Image.open(os.path.join(app_root, 'images', 'Cropped', image_name))
        image = image.crop((left, top, right, bottom))
        image = image.resize((pixels, pixels), Image.ANTIALIAS)
        image = np.array(image)

        if (image_name == "g1.jpg"):
            data_white_kingside.append(image) 
        if (image_name == "c1.jpg"):
            data_white_queenside.append(image) 
        if (image_name == "g8.jpg"):
            data_black_kingside.append(image) 
        if (image_name == "c8.jpg"):
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
        if (kingside == 'true' and queenside == 'true'):
            castling_predictions_kingside = model.predict(data_white_kingside)
            castling_predictions_queenside = model.predict(data_white_queenside)
            probability_kingside = max([castling_predictions_kingside[0][0], castling_predictions_kingside[0][1], castling_predictions_kingside[0][3], castling_predictions_kingside[0][4]])
            probability_queenside = max([castling_predictions_queenside[0][0], castling_predictions_queenside[0][1], castling_predictions_queenside[0][3], castling_predictions_queenside[0][4]])
            max_probability = max(probability_kingside, probability_queenside)
            if (max_probability > threshold):
               if (max_probability == probability_kingside):
                   return "h1*"
               else:
                   return "a1*"

        if (kingside == 'true'):
            castling_predictions_kingside = model.predict(data_white_kingside)
            probability_kingside = max([castling_predictions_kingside[0][0], castling_predictions_kingside[0][1], castling_predictions_kingside[0][3], castling_predictions_kingside[0][4]])
            if (probability_kingside > threshold):
               return "h1*"
        if (queenside == 'true'):
            castling_predictions_queenside = model.predict(data_white_queenside)
            probability_queenside = max([castling_predictions_queenside[0][0], castling_predictions_queenside[0][1], castling_predictions_queenside[0][3], castling_predictions_queenside[0][4]])
            if (probability_queenside > threshold):
               return "a1*"
           
    else:
        first = 1
        second = 4

        # Check if castling move has been made
        if (kingside == 'true' and queenside == 'true'):
            castling_predictions_kingside = model.predict(data_black_kingside)
            castling_predictions_queenside = model.predict(data_black_queenside)
            probability_kingside = max([castling_predictions_kingside[0][0], castling_predictions_kingside[0][1], castling_predictions_kingside[0][3], castling_predictions_kingside[0][4]])
            probability_queenside = max([castling_predictions_queenside[0][0], castling_predictions_queenside[0][1], castling_predictions_queenside[0][3], castling_predictions_queenside[0][4]])
            max_probability = max(probability_kingside, probability_queenside)
            if (max_probability > threshold):
               if (max_probability == probability_kingside):
                   return "h8*"
               else:
                   return "a8*"

        if (kingside == 'true'):
            castling_predictions_kingside = model.predict(data_black_kingside)
            probability_kingside = max([castling_predictions_kingside[0][0], castling_predictions_kingside[0][1], castling_predictions_kingside[0][3], castling_predictions_kingside[0][4]])
            if (probability_kingside > threshold):
               return "h8*"
        if (queenside == 'true'):
            castling_predictions_queenside = model.predict(data_black_queenside)
            probability_queenside = max([castling_predictions_queenside[0][0], castling_predictions_queenside[0][1], castling_predictions_queenside[0][3], castling_predictions_queenside[0][4]])
            if (probability_queenside > threshold):
               return "a8*"

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

