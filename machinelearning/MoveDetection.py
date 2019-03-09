import sys
import cv2
import glob
from BoardDetection import segmentation_board as find_corners
from Crop import crop_squares
from Initialize import load_weights
from Initialize import initialize_fen
from detectEmpty import detect_empty
from detectMove import detect_move

def main(argv):
    # Controls all other functions

    # Take last image from the webcam
    paths = glob.glob('images*.jpg')
    img_path = paths[len(paths) - 1]
    image = cv2.imread(img_path)

    # Board segmentation
    (list1, list2) = find_corners(image)
    image = image[list1[1]:list2[1], list1[0]:list2[0]]
    cv2.imwrite(img_path, image)

    # Crop the board into 64 squares
    crop_squares(img_path)

    # Load the weights for the neural network model
    model = load_weights()

    #Initialize board state using FEN notation
    initialize_fen()

    # Move detection
    ## Detect the most probable origin square
    (empty_square, piece, new_fen) = detect_empty(model)
    ## Detect the most probable destination square
    piece_position = detect_move(model, piece, new_fen)
    print(('{} moved from {} to {}').format(piece, empty_square, piece_position))

if __name__=="__main__":
    main(sys.argv[1:])