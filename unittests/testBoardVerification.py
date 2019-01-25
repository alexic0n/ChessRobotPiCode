import unittest

from classes.boardState import *

class BoardVerification(unittest.TestCase):

    def testBoardVerification(self):
        board = BoardState()
        ambiguousBoard = [
            "bbbbbbbb",
            "bbbbbbbb",
            "********",
            "********",
            "********",
            "********",
            "wwwwwwww",
            "wwwwwwww"
        ]
        self.assertTrue(board.verifyState(ambiguousBoard))

        
# required setup for testing
if __name__ == '__main__':
    unittest.main(exit=False)
