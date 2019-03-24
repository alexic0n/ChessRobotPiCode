from util.planner import *
from util.util import *

def planSimple(position):
    return plan(
        position,
        "********/********/********/********/********/********/********/********",
        None,
        {"left": -6.25, "right": 106.25, "top": -6.25, "bottom": 106.25},
        "-"
    )

moves = []

# open file and read the content in a list
with open('games/last.txt', 'r') as filehandle:
    moves = [current_place.rstrip() for current_place in filehandle.readlines()]

for move in moves:
    # print(move)
    planSimple(move)