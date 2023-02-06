import numpy as np
from Constants import *

class Board():
    def __init__(self):
        self.piece_bbs = np.zeros((2,6), dtype=np.uint64)
        self.color_occ = np.zeroes(2, dtype=np.uint64)
        self.occ = np.zeros(1, dtype=np.uint64)

    def convert_bb_to_readable(self):
        pass