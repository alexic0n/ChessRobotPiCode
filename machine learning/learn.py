import falcon
import json
import mimetypes
import io
import os
import uuid
import sys
import cv2
import glob
from BoardDetection import segmentation_board as find_corners
from Crop import crop_squares
from Initialize import load_weights
from Initialize import initialize_fen
from detectEmpty import detect_empty
from detectMove import detect_move

from model import model

class LearnResource(object):
  def on_post(self, req, resp):
    """ POST /position: 
        Asks the hardware to move the gantry to the requested position
        in mm."""

    print("[POST] /learn")

    if req.content_length in (None, 0):
      # Nothing to do
      return

    name = '{uuid}.jpg'.format(uuid=uuid.uuid4())

    storage_path = './Logitech Webcam'

    image_path = os.path.join(storage_path, name)

    with io.open(image_path, 'wb') as image_file:
      while True:
        chunk = req.stream.read(4096)
        if not chunk:
          break

        image_file.write(chunk)
    
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
    (empty_square, piece, new_fen) = detect_empty(model)
    ## Detect the most probable destination square
    piece_position = detect_move(model, piece, new_fen)
    print(('{} moved from {} to {}').format(piece, empty_square, piece_position))

    resp.status = falcon.HTTP_201
    with open('./Board State/previousFEN.txt') as r:
      resp.body = '{} moved from {} to {}\n{}'.format(piece, empty_square, piece_position, r.read())
