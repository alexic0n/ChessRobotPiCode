from util.util import *
from classes.move import *

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
        self.enpassant = "-"

    def applyMove(self, move):

        # check correct piece
        # boardPiece = self.getPieceAt(move.start)
        # if (boardPiece != move.piece):
        #     raise ValueError("Cannot apply move, piece is %s but move is %s", boardPiece, move.toString())

        # if (not move.isLegal()): raise ValueError("Move is illegal.", move.toString())

        # if (self.getPieceAt(move.to) != "*"):
        #     raise ValueError("Must move to an empty square.", move.toString())
        # print(move.toString())
        piece = self.getPieceAt(move.start)

        rookMove = self.castlingMove(move)
        if (rookMove != None):
            print("Castling!")
            self.applyMove(rookMove)

        # enpassant = self.enpassantSquare(move)
        # if (enpassant and enpassant["enpassant"] == move.to):
        #     print("Enpassant!")
        #     self.setPiece("*", enpassant["pawn"])
        
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

    def castlingMove(self, move):
        piece = self.getPieceAt(move.start)
        if (piece != "k" and piece != "K"):
            return None

        # bottom left
        if (move.start == {"x": 0, "y": 3} and move.to == {"x": 0, "y": 1}): 
            return Move({"x": 0, "y": 0}, {"x": 0, "y": 2})
        if (move.start == {"x": 0, "y": 4} and move.to == {"x": 0, "y": 2}): 
            return Move({"x": 0, "y": 0}, {"x": 0, "y": 3})

        # bottom right
        if (move.start == {"x": 0, "y": 3} and move.to == {"x": 0, "y": 5}): 
            return Move({"x": 0, "y": 7}, {"x": 0, "y": 4})
        if (move.start == {"x": 0, "y": 4} and move.to == {"x": 0, "y": 6}): 
            return Move({"x": 0, "y": 7}, {"x": 0, "y": 5})
            
        # bottom left
        if (move.start == {"x": 7, "y": 3} and move.to == {"x": 7, "y": 1}): 
            return Move({"x": 7, "y": 0}, {"x": 7, "y": 2})
        if (move.start == {"x": 7, "y": 4} and move.to == {"x": 7, "y": 2}): 
            return Move({"x": 7, "y": 0}, {"x": 7, "y": 3})

        # bottom right
        if (move.start == {"x": 7, "y": 3} and move.to == {"x": 7, "y": 5}): 
            return Move({"x": 7, "y": 7}, {"x": 7, "y": 4})
        if (move.start == {"x": 7, "y": 4} and move.to == {"x": 7, "y": 6}): 
            return Move({"x": 7, "y": 7}, {"x": 7, "y": 5})

        return None

    def enpassantSquare(self, move):
        piece = self.getPieceAt(move.start)
        if (piece != "p" and piece != "P"):
            return None

        startX = move.start["x"]
        startY = move.start["y"]
        endX   = move.to["x"]
        endY   = move.to["y"]

        if (startX == 1 and endX == 3 and startY == endY):
            return {"enpassant": {"x": 2, "y": startY}, "pawn": {"x": 3, "y": startY}}

        if (startX == 6 and endX == 4 and startY == endY):
            return {"enpassant": {"x": 5, "y": startY}, "pawn": {"x": 4, "y": startY}}

        return None

    def printState(self):
        for row in self.state:
            print(row)
        print()

    def getPieceAt(self, pos):
        x = 7 - pos["x"]
        y = pos["y"]
        return self.state[x][y]

    def setPiece(self, piece, pos):
        row = self.state[7 - pos["x"]]
        y = pos["y"]
        row = row[:y] + piece + row[(y+1):]
        self.state[7 - pos["x"]] = row