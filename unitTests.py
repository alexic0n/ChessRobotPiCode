import unittest

from classes.move import Move

class UnitTests(unittest.TestCase):

    def test(self):
        move = Move("K", "A1", "A2")
        self.assertEqual(move.isLegal(), None)

# required setup for testing
if __name__ == '__main__':
    unittest.main(exit=False)
