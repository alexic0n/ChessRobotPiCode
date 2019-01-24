class Move:
    def __init__(self, piece, start, to):
        self.piece = piece  # char
        self.start = start  # dict: {x, y}
        self.to = to        # dict: {x, y}
    
    def isLegal(self):
        # TODO - check with the chess AI
        return True

    def toString(self):
        return f"Move: {self.piece} from {self.start} to {self.to}"