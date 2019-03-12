from util.planner import *
from util.util import *

KNIGHT_POSITIONS = [[0, 0], [2, 1], [4, 0], [6, 1], [7, 3], [6, 5], [7, 7], [5, 6], [7, 5], [6, 7], [4, 6], [2, 7], [0, 6], [1, 4], [0, 2], [1, 0], [3, 1], [5, 0], [7, 1], [6, 3], [4, 2], [3, 0], [1, 1], [0, 3], [2, 2], [0, 1], [2, 0], [1, 2], [0, 4], [2, 3], [1, 5], [0, 7], [2, 6], [4, 7], [6, 6], [7, 4], [6, 2], [7, 0], [5, 1], [7, 2], [6, 0], [4, 1], [5, 3], [3, 4], [5, 5], [7, 6], [5, 7], [3, 6], [1, 7], [0, 5], [1, 3], [3, 2], [4, 4], [5, 2], [6, 4], [4, 3], [3, 5], [5, 4], [3, 3], [2, 5], [3, 7], [4, 5], [2, 4], [1, 6]]

# EXAMPLE USES #################################################################

# in these examples the board is 8x8 units big, with the top left corner being 0,0
# to represent a piece being off-centre x.51 is used, the planner will then place pieces
# exactly at x.5

def planSimple(position):
    return plan(
        position,
        "********/********/********/********/********/********/********/********",
        None,
        {"left": 0, "right": 100, "top": 0, "bottom": 100},
        "-"
    )

print("Starting Knight's tour...")
# planSimple("a1b3")
# planSimple("b3c1")

prevPos = KNIGHT_POSITIONS[0]
for pos in KNIGHT_POSITIONS[1:]:
    posName = coordinatesToSquare({"x": pos[0], "y": pos[1]})
    prevPosName = coordinatesToSquare({"x": prevPos[0], "y": prevPos[1]})
    # print(prevPosName + posName)
    planSimple(prevPosName + posName)
    prevPos = pos
