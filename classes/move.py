class Move:
    def __init__(self, start, to):
        # self.piece = piece  # char
        self.start = start  # dict: {x, y}
        self.to = to        # dict: {x, y}
    
    def isLegal(self):
        # TODO - check with the chess AI
        return True

    def toString(self):
        return "Move: from {} to {}".format(self.start, self.to)