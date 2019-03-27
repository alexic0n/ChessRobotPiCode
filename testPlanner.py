from util.planner import *

# EXAMPLE USES #################################################################

# in these examples the board is 8x8 units big, with the top left corner being 0,0
# to represent a piece being off-centre x.51 is used, the planner will then place pieces
# exactly at x.5

print("\nNORMAL MOVE NO PIECE TAKEN:")
plan(
    move="a2a4"
)

print("\nTAKE PIECE:")
plan(
    move="b3a4",
    board="rnbqkbnr/*ppppppp/********/********/p*******/*P******/P*PPPPPP/RNBQKBNR"
)

print("\nEN PASSANT:")
plan(
    move="b4a3",
    board="rnbqkbnr/p*pppppp/********/********/Pp******/********/*PPPPPPP/RNBQKBNR",
    enpassant="a3"
)

print("\nEN PASSANT THE OTHER WAY:")
plan(
    move="a5b6",
    board="rnbqkbnr/p*pppppp/********/Pp******/********/********/*PPPPPPP/RNBQKBNR",
    enpassant="b6"
)

print("\nCASTLING RIGHT TOP:")
plan(
    move="e8g8",
    board="rnbqk**r/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR"
)

print("\nCASTLING LEFT TOP:")
plan(
    move="e8c8",
    board="r***kbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQKBNR"
)

print("\nCASTLING RIGHT BOTTOM:")
plan(
    move="e1g1",
    board="rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/RNBQK**R"
)

print("\nCASTLING LEFT BOTTOM:")
plan(
    move="e1c1",
    board="rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/R***KBNR"
)

print("\nCASTLING LEFT BOTTOM ALTERNATIVE NOTATION:")
plan(
    move="e1a1",
    board="rnbqkbnr/pppppppp/********/********/********/********/PPPPPPPP/R***KBNR"
)
