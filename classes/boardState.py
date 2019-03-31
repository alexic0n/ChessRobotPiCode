from util.util import *

class BoardState:

    def __init__(self):
        # initial starting board
        self.state = [
            "rnbqkbnr",
            "pppppppp",
            "********",
            "********",
            "********",
            "********",
            "PPPPPPPP",
            "RNBQKBNR"
        ]

    def applyMove(self, move):

        # check correct piece
        # boardPiece = self.getPieceAt(move.start)
        # if (boardPiece != move.piece):
        #     raise ValueError("Cannot apply move, piece is %s but move is %s", boardPiece, move.toString())

        # if (not move.isLegal()): raise ValueError("Move is illegal.", move.toString())

        # if (self.getPieceAt(move.to) != "*"):
        #     raise ValueError("Must move to an empty square.", move.toString())
        piece = self.getPieceAt(move.start)
        self.setPiece("*", move.start)
        self.setPiece(piece, move.to)
    
    def verifyState(self, ambiguousBoard):
        for row in range(8):
            for col in range(8):
                ambiguous = ambiguousBoard[row][col]
                state = self.state[row][col]
                if (ambiguous == "b" and not state.islower()): return False
                if (ambiguous == "w" and not state.isupper()): return False
                if (ambiguous == "*" and not state == "*"): return False

        return True

    def printState(self):
        print(self.state)

    def getPieceAt(self, pos):
        x = 7 - pos["x"]
        y = pos["y"]
        return self.state[x][y]

    def setPiece(self, piece, pos):
        row = self.state[7 - pos["x"]]
        y = pos["y"]
        row = row[:y] + piece + row[(y+1):]
        self.state[7 - pos["x"]] = row