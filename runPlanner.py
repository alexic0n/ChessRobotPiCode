from util.planner import *

# EXAMPLE USES #################################################################

# in these examples the board is 8x8 units big, with the top left corner being 0,0
# to represent a piece being off-centre x.51 is used, the planner will then place pieces
# exactly at x.5

print("\nNORMAL MOVE:")
actions = plan(
    "a2a4",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR",
    {"a2": {"x": 0.51, "y": 6.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nTAKE PIECE:")
actions = plan(
    "b3a4",
    "rnbqkbnr/*ppppppp/********/********/p*******/*P******/P*PPPPPP/RNBQKBNR",
    {"b3": {"x": 1.51, "y": 5.51}, "a4": {"x": 0.51, "y": 4.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nTAKE PIECE WITH NO PIECE LOC:")
actions = plan(
    "b3a4",
    "rnbqkbnr/*ppppppp/********/********/p*******/*P******/P*PPPPPP/RNBQKBNR",
    None,
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nEN PASSANT:")
actions = plan(
    "b4a3",
    "rnbqkbnr/p*pppppp/********/********/Pp******/********/*PPPPPPP/RNBQKBNR",
    {"a4": {"x": 0.51, "y": 4.51}, "b4": {"x": 1.51, "y": 4.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "a3"
)
print("Actions:")
for action in actions: print(action)


print("\nEN PASSANT THE OTHER WAY:")
actions = plan(
    "a5b6",
    "rnbqkbnr/p*pppppp/********/Pp******/********/********/*PPPPPPP/RNBQKBNR",
    {"a5": {"x": 0.51, "y": 3.51}, "b5": {"x": 1.51, "y": 3.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "b6"
)
print("Actions:")
for action in actions: print(action)


print("\nCASTLING RIGHT TOP:")
actions = plan(
    "e8g8",
    "rnbqk**r/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR",
    {"e8": {"x": 4.51, "y": 0.51}, "h8": {"x": 7.51, "y": 0.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nCASTLING LEFT TOP:")
actions = plan(
    "e8c8",
    "r***kbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR",
    {"e8": {"x": 4.51, "y": 0.51}, "a8": {"x": 0.51, "y": 0.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nCASTLING RIGHT BOTTOM:")
actions = plan(
    "e1g1",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQK**R",
    {"e1": {"x": 4.51, "y": 7.51}, "h1": {"x": 7.51, "y": 7.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nCASTLING LEFT BOTTOM:")
actions = plan(
    "e1c1",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/R***KBNR",
    {"e1": {"x": 4.51, "y": 7.51}, "a1": {"x": 0.51, "y": 7.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)


print("\nUNUSUAL CASTLING:")
actions = plan(
    "g1e1",
    "rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/*R****K*",
    {"g1": {"x": 6.51, "y": 7.51}, "b1": {"x": 1.51, "y": 7.51}},
    {"left": 0, "right": 8, "top": 0, "bottom": 8},
    "-"
)
print("Actions:")
for action in actions: print(action)