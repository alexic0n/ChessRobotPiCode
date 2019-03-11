from util.planner import *

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
planSimple("a1b3")
planSimple("b3c1")