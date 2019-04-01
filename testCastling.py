from classes.boardState import *
from classes.move import *
from util.util import *

def apply(boardState, moveStr):
    moveDictFrom = squareToCoordinates(moveStr[0:2], "w")
    moveDictTo   = squareToCoordinates(moveStr[2:4], "w")
    moveObj = Move(moveDictFrom, moveDictTo)  
    boardState.applyMove(moveObj)

print("Castling bottom left")
boardState = BoardState()
apply(boardState, "b1b3")
apply(boardState, "c1c3")
apply(boardState, "d1d3")
apply(boardState, "e1c1")
boardState.printState()

print("Castling bottom right")
boardState = BoardState()
apply(boardState, "f1f3")
apply(boardState, "g1g3")
apply(boardState, "e1g1")
boardState.printState()

print("Castling bottom left")
boardState = BoardState()
apply(boardState, "b8b6")
apply(boardState, "c8c6")
apply(boardState, "d8d6")
apply(boardState, "e8c8")
boardState.printState()

print("Castling bottom right")
boardState = BoardState()
apply(boardState, "f8f6")
apply(boardState, "g8g6")
apply(boardState, "e8g8")
boardState.printState()

print("Enpassant")
boardState = BoardState()
apply(boardState, "a1a5")
boardState.printState()
apply(boardState, "b7b5")
boardState.printState()
apply(boardState, "a5b6")
boardState.printState()