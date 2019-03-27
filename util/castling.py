# given the move for the king, return the move that the rook needs to make
def castlingRookMove(move):

    if (move == "e8g8"): return {
        "from": {"x": 7, "y": 0},
        "to":   {"x": 5, "y": 0}
    }

    if (move == "e8c8"): return {
        "from": {"x": 0, "y": 0},
        "to":   {"x": 2, "y": 0}    
    }

    if (move == "e1g1"): return {
        "from": {"x": 7, "y": 7},
        "to":   {"x": 5, "y": 7}
    }

    if (move == "e1c1"): return {
        "from": {"x": 0, "y": 7},
        "to":   {"x": 2, "y": 7}
    }

    return None
