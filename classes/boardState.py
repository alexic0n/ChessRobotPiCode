class BoardState:

    def __init__(self, state):
        self.state = state

    def applyMove(self, move):
        pass
    
    def verifyState(self, ambiguousBoard):
        pass

    def printState(self):
        print(self.state)