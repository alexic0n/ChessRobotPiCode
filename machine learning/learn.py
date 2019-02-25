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

    img_path = os.path.join(storage_path, name)

    with io.open(img_path, 'wb') as image_file:
        image_file.write(req.get_param('img'))
    
    # Controls all other functions

    # Crop the board into 64 squares
    crop_squares(img_path)

    # Initialize board state using FEN notation
    fen_notation = req.get_param('fen')
    legalmoves = req.get_param('moves')

    # Move detection
    ## Detect the most probable origin square
    (empty_square, piece, new_fen) = detect_empty(model, fen_notation)
    ## Detect the most probable destination square
    new_fen, piece_position = detect_move(model, piece, empty_square, new_fen, legalmoves)
    print(('{} moved from {} to {}').format(piece, empty_square, piece_position))

    resp.status = falcon.HTTP_201
    resp.body = json.dumps({
      'fen': new_fen,
      'status': '{} moved from {} to {}'.format(piece, empty_square, piece_position)
    })
