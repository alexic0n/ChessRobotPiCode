import unittest
from move import *

class UnitTests(unittest.TestCase):

    def test(self):
        move = Move("K", "A1", "A2")
        self.assertEqual(move.isLegal(), None)
        self.assertEqual(move.piece, "K")
        self.assertEqual(move.moveTo, "A2")

if __name__ == '__main__':
    unittest.main(exit=False)
