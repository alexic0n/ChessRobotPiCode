import unittest

import sys
sys.path.append('C:/Users/felix/Documents/SDP pi/classes')

from boardState import *
from move import *

class UnitTests(unittest.TestCase):

    def testApplyMove(self):

        # if the applyMove method does not throw an error, the test will fail
        def expectError(move):
            try:
                BoardState().applyMove(move)
                # applyMove will fail so this assertion will not be seen
                self.assertFalse(f"Apply move succeeded when it should have failed. {move.toString()}")
            except: pass
                
        expectError(Move("p", {'x': 0, 'y': 2}, {'x': 0, 'y': 3}))  # wrong piece
        expectError(Move("p", {'x': 0, 'y': 1}, {'x': 0, 'y': 1}))  # start == to
        expectError(Move("p", {'x': 0, 'y': 1}, {'x': 0, 'y': -1})) # off the board
        expectError(Move("p", {'x': 0, 'y': 1}, {'x': 1, 'y': 1}))  # move.to not empty

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
