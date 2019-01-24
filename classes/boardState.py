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
        pass

    def printState(self):
        print(self.state)

    def getPieceAt(self, square):
        pass