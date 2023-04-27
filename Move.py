from Bitboard import *


class Move():
    def __init__(self, coord_from=None, coord_to=None, index_from=None, index_to=None, en_passant=False, promo=None, is_capture=False):
        self.coord_from = coord_from
        self.coord_to = coord_to

        self.index_from = index_from
        self.index_to = index_to

        self.en_passant = en_passant

        self.promo = promo
        self.is_capture = is_capture

    def __str__(self):
        return f"Move from {self.coord_from}/{self.index_from} to {self.coord_to}/{self.index_to}"

    def __repr__(self):
        return f"Move from {self.coord_from}/{self.index_from} to {self.coord_to}/{self.index_to}"

    def set_coord_from(self, coord):
        self.coord_from = coord
        self.index_from = convert_row_col_to_index(*coord)

    def set_coord_to(self, coord):
        self.coord_to = coord
        self.index_to = convert_row_col_to_index(*coord)


class Castle(Move):
    def __init__(self, king_index_from=None, king_index_to=None, rook_index_from=None, rook_index_to=None):
        super().__init__(index_from=king_index_from, index_to=king_index_to)
        self.king_move = Move(index_from=king_index_from,index_to=king_index_to)
        self.rook_move = Move(index_from=rook_index_from, index_to=rook_index_to)
