CheckMate TensorFlow endpoint
=============

This endpoint is used to access the TensorFlow based piece detection engine from the Pi.

Setup
----

  1. **Install dependencies**: nice and easy, we have pip. `pip install -r requirements.txt`
  2. **Start Flask**: currently on the development server, which isn't ideal, but it does the trick:
     `python web.py`

That's it.

Endpoint
----

It expects a multipart form with the following components:

  - **fen**: the current state of the board in FEN notation
  - **validmoves**: list of legal moves
  - **board**: .jpg of the current board to be processed

It will return something based off this string construction:

    response = '{} moved from {} to {}\n{}'.format(piece, empty_square, piece_position, new_fen)

File locations
----

Everything you need is in `web.py`, it just pulls in code from the rest of the project, based off `BoardDetection.py`.
