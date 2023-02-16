from enum import IntEnum
import numpy as np

WIDTH = 600
HEIGHT = 600

SQUARE_SIZE = WIDTH / 8

EMPTY_BB = np.uint64(0)
class Color(IntEnum):
    WHITE=0
    BLACK=1

class Castling(IntEnum):
    QUEENSIDE=0
    KINGSIDE=1
class Piece(IntEnum):
    PAWN=0
    ROOK=1
    KNIGHT=2
    BISHOP=3
    QUEEN=4
    KING=5

    def to_char(self):
        if self == Piece.PAWN:
            return 'p'
        elif self == Piece.KNIGHT:
            return 'n'
        elif self == Piece.BISHOP:
            return 'b'
        elif self == Piece.ROOK:
            return 'r'
        elif self == Piece.QUEEN:
            return 'q'
        elif self == Piece.KING:
            return 'k'


class Rank(IntEnum):
    ONE = 0
    TWO = 1
    THREE = 2
    FOUR = 3
    FIVE = 4
    SIX = 5
    SEVEN = 6
    EIGHT = 7

class File(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7

class PawnMoveType(IntEnum):
    NORMAL = 0
    ATTACK = 1

class GameState(IntEnum):
    NORMAL = 0
    STALEMATE = 1
    CHECKMATE = 2

