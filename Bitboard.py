import numpy as np
from Constants import *

debruijn = np.uint64(0x03f79d71b4cb0a89)

lsb_lookup = np.array(
        [ 0,  1, 48,  2, 57, 49, 28,  3,
         61, 58, 50, 42, 38, 29, 17,  4,
         62, 55, 59, 36, 53, 51, 43, 22,
         45, 39, 33, 30, 24, 18, 12,  5,
         63, 47, 56, 27, 60, 41, 37, 16,
         54, 35, 52, 21, 44, 32, 23, 11,
         46, 26, 40, 15, 34, 20, 31, 10,
         25, 14, 19,  9, 13,  8,  7,  6],
        dtype=np.uint64)

msb_lookup = np.array(
        [ 0, 47,  1, 56, 48, 27,  2, 60,
         57, 49, 41, 37, 28, 16,  3, 61,
         54, 58, 35, 52, 50, 42, 21, 44,
         38, 32, 29, 23, 17, 11,  4, 62,
         46, 55, 26, 59, 40, 36, 15, 53,
         34, 51, 20, 43, 31, 22, 10, 45,
         25, 39, 14, 33, 19, 30,  9, 24,
         13, 18,  8, 12,  7,  6,  5, 63],
        dtype=np.uint64)

def to_bitboard(i):
    """
    Sets 64-bit number with bit at index `i` set to 1
    :param index:
    :return:
    """
    return np.uint64(1) << np.uint64(i)

def get_occupied_squares(bb):
    """
    Returns indexes of bits set to 1 in 64-bit number bb
    :param bb:
    :return:
    """
    idxs = []
    while bb != EMPTY_BB:
        lsb_square = lsb_bitscan(bb)
        idxs.append(lsb_square)
        bb ^= to_bitboard(lsb_square)
    return idxs

def convert_index_to_row_col(idx):
    return (int(idx // 8), int(idx % 8))

def convert_row_col_to_index(row, col):
    return row * 8 + col

def lsb_bitscan(bb):
    return lsb_lookup[((bb & -bb) * debruijn) >> np.uint64(58)]

def msb_bitscan(bb):
    bb |= bb >> np.uint8(1)
    bb |= bb >> np.uint8(2)
    bb |= bb >> np.uint8(4)
    bb |= bb >> np.uint8(8)
    bb |= bb >> np.uint8(16)
    bb |= bb >> np.uint8(32)
    return msb_lookup[(bb * debruijn) >> np.uint64(58)]

def is_set(square, bb):
    return to_bitboard(square) & bb != EMPTY_BB
def set_square(square, bb):
    return to_bitboard(square) | bb

def clear_square(square, bb):
    return (~to_bitboard(square)) & bb
