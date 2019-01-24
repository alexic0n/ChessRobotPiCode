import sys
sys.path.append('python-chess-master')
import chess
import chess.engine

##This class takes a black and white representation of the board and comapres it with possible states after a legal move
##Once vision is working, an input such as bbb/bb3... can be parsed and compared, and the games inetrnal state is updated, followed by the ai making a move

class ChessMatch:

    def __init__(self,thinkTime):
        self.limit = chess.engine.Limit(time = thinkTime)
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci("/home/student/ChessBotTest/stockfish")

    def endgame(self):
        self.engine.quit()

    def aiTurn(self):
        a = self.engine.play(self.board,self.limit).move
        self.board.push(a)
        return a

    def userTurn(self, updatedBoardFen):
        legalMoves = self.board.legal_moves
        for a in legalMoves:
            self.board.push(a)
            if(updatedBoardFen == self.convertBW(self.board.fen())):
                return True
            self.board.pop()
        return False

    def convertBW(self, toConv):
        boardState = toConv.split(' ')[0]
        forRet = ''
        counter = 0
        while(counter < len(boardState)):
            if(boardState[counter].isupper()):
                forRet = forRet + 'w'
            else:
                if(boardState[counter].islower()):
                     forRet = forRet + 'b'
                else:
                    forRet = forRet + boardState[counter]
            counter = counter + 1
        print(forRet)
        return forRet
