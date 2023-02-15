from Bitboard import *


class Move():
    def __init__(self, coord_from=None,  coord_to=None, index_from=None, index_to=None):
        self.coord_from = coord_from
        self.coord_to = coord_to

        self.index_from = index_from
        self.index_to = index_to

    def __str__(self):
        return f"Move from {self.coord_from}/{self.index_from} to {self.coord_to}/{self.index_to}"

    def set_coord_from(self, coord):
        self.coord_from = coord
        self.index_from = convert_row_col_to_index(*coord)

    def set_coord_to(self, coord):
        self.coord_to = coord
        self.index_to = convert_row_col_to_index(*coord)