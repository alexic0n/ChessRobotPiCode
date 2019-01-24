class Move:
    def __init__(self, piece, moveFrom, moveTo):
        self.piece = piece
        self.moveFrom = moveFrom
        self.moveTo = moveTo
    
    def isLegal(self):
        # TODO - check with the chess AI
        pass