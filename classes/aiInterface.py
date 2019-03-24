import sys
sys.path.append("../util/pythonchess")
import chess
import chess.engine

##This class takes a black and white representation of the board and comapres it with possible states after a legal move
##Once vision is working, an input such as bbb/bb3... can be parsed and compared, and the games inetrnal state is updated, followed by the ai making a move

class ChessMatch:

    def __init__(self, depth):
        self.limit = chess.engine.Limit(depth = depth)
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci("/home/student/MachineLearning/pi/util/stockfish")

    def endgame(self):
        self.engine.quit()

    def aiTurn(self):
        a = self.engine.play(self.board,self.limit).move
        if not (a==None):
            self.board.push(a)
        return a

    def userTurn(self, a):
            self.board.push(a)

    def convertBW(self, toConv):
        boardState = toConv.split(' ')[0]
        forRet = ''
        counter = 0
        while(counter < len(boardState)):
            current = boardState[counter]
            if(current.isupper()):
                forRet = forRet + 'w'
            elif(current.islower()):
                forRet = forRet + 'b'
            elif(current in '12345678'):
                aster = int(current)
                while(aster > 0):
                    forRet = forRet + '*'
                    aster = aster - 1
            else:
                forRet = forRet + boardState[counter]
            counter = counter + 1
        return forRet

    def convertToFenWithSpaces(self, fen):
        boardState = fen.split(' ')[0]
        out = ""
        for char in boardState:
            if char in "12345678":
                out += "*" * int(char)
            else:
                out += char
        return out
