import sys
sys.path.append("../util/pythonchess")
import chess
import chess.engine

##This class takes a black and white representation of the board and comapres it with possible states after a legal move
##Once vision is working, an input such as bbb/bb3... can be parsed and compared, and the games inetrnal state is updated, followed by the ai making a move

class ChessMatch:

    def __init__(self,thinkTime):
        self.limit = chess.engine.Limit(time = thinkTime)
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci("/home/student/ChessBot/util/stockfish")

    def endgame(self):
        self.engine.quit()

    def aiTurn(self):
        a = self.engine.play(self.board,self.limit).move
        self.board.push(a)
        return a

    def userTurn(self, empty_square):
        legalMoves = self.board.legal_moves
        legalDestinations = []
        for element in legalMoves:
            if element[0:2] == empty_square:
                legalDestinations.append(element[2:4])

        if len(legalDestinations) == 0:
            return False, []
        else:
            return True, legalDestinations
