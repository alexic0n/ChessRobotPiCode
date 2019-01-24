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
        pass
    
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
        x = pos["x"]
        y = pos["y"]
        return self.state[y][x]