import unittest
from move import Move

class UnitTests(unittest.TestCase):

    def testLegalMove(self):
        move = Move("K", "A1", "A2")
        self.assertEqual(move.isLegal(), None)

if __name__ == '__main__':
    unittest.main(exit=False)
