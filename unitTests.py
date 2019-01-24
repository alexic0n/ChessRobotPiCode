import unittest

from classes.boardState import *
from classes.move import *

class UnitTests(unittest.TestCase):

    def test(self):
        move = Move("K", "A1", "A2")
        self.assertEqual(move.isLegal(), None)

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
