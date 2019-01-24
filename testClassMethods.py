import unittest

from classes.boardState import *
from classes.move import *

class UnitTests(unittest.TestCase):

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

    def testApplyMove(self):

        def shouldFail(move):
            try:
                BoardState().applyMove(move)
                # applyMove will fail so this assertion will not be seen
                self.assertFalse(f"Apply move succeeded when it should have failed. {move.toString()}")
            except: pass
                
        shouldFail(Move("p", {'x': 0, 'y': 2}, {'x': 0, 'y': 3})) # wrong piece
        shouldFail(Move("p", {'x': 0, 'y': 1}, {'x': 0, 'y': 1})) # start == to
        shouldFail(Move("p", {'x': 0, 'y': 1}, {'x': 0, 'y': 1})) # start == to

        board = BoardState()
        board.applyMove(Move("p", {'x': 0, 'y': 1}, {'x': 0, 'y': 3}))
        self.assertEqual(board.state, [
            "rnbqkbnr",
            "*ppppppp",
            "********",
            "p*******",
            "********",
            "********",
            "PPPPPPPP",
            "RNBQKBNR"
        ])
        board.applyMove(Move("N", {'x': 1, 'y': 7}, {'x': 2, 'y': 5}))
        self.assertEqual(board.state, [
            "rnbqkbnr",
            "*ppppppp",
            "********",
            "p*******",
            "********",
            "**N*****",
            "PPPPPPPP",
            "R*BQKBNR"
        ])

        
# required setup for testing
if __name__ == '__main__':
    unittest.main(exit=False)
