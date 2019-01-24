# import files like this
from classes.boardState import *
from util.util import *

board = BoardState()
board.printState()

print(squareToCoordinates("a1"))
print(squareToCoordinates("H8"))

print(board.getPieceAt({"x": 0, "y": 0}))