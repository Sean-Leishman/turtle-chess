import numpy as np
from Constants import *
from MoveGeneration import MoveGenerator
from Bitboard import *
class FormattedBoard():
    def __init__(self):
        self.board = [[None] * 8 for i in range(8)]
        self.legal_moves = [[[] for j in range(8)] for i in range(8)]

    def get_board(self):
        return self.board
    def update_board(self, bb):
        for color in Color:
            for piece in Piece:
                for src in get_occupied_squares(bb[color][piece]):
                    row, col = convert_index_to_row_col(src)
                    self.board[row][col] = (color, piece)

    def get_legal_moves(self):
        return self.legal_moves
    def update_legal_moves(self, bbs):
        for idx, bb in enumerate(bbs):
            if bb > 0:
                print(bb)
                row, col = convert_index_to_row_col(idx)
                print(row, col)
                self.legal_moves[row][col] = list(map(lambda x: convert_index_to_row_col(x), get_occupied_squares(bb)))

class Board():
    def __init__(self):
        self.piece_bb = np.zeros((2,6), dtype=np.uint64)
        self.color_occ = np.zeros(2, dtype=np.uint64)
        self.occ = np.zeros(1, dtype=np.uint64)
        self.move_generator = MoveGenerator()
        self.color = Color.WHITE

        self.format_board = FormattedBoard()
        self.legal_moves = None

    def initialise_boards(self):
        self.piece_bb[Color.WHITE][Piece.PAWN] = np.uint64(0x000000000000FF00)
        self.piece_bb[Color.WHITE][Piece.KNIGHT] = np.uint64(0x0000000000000042)
        self.piece_bb[Color.WHITE][Piece.BISHOP] = np.uint64(0x0000000000000024)
        self.piece_bb[Color.WHITE][Piece.ROOK] = np.uint64(0x0000000000000081)
        self.piece_bb[Color.WHITE][Piece.QUEEN] = np.uint64(0x0000000000000008)
        self.piece_bb[Color.WHITE][Piece.KING] = np.uint64(0x0000000000000010)

        self.piece_bb[Color.BLACK][Piece.PAWN] = np.uint64(0x00FF000000000000)
        self.piece_bb[Color.BLACK][Piece.KNIGHT] = np.uint64(0x4200000000000000)
        self.piece_bb[Color.BLACK][Piece.BISHOP] = np.uint64(0x2400000000000000)
        self.piece_bb[Color.BLACK][Piece.ROOK] = np.uint64(0x8100000000000000)
        self.piece_bb[Color.BLACK][Piece.QUEEN] = np.uint64(0x0800000000000000)
        self.piece_bb[Color.BLACK][Piece.KING] = np.uint64(0x1000000000000000)

        for p in Piece:
            for c in Color:
                self.color_occ[c] |= self.piece_bb[c][p]

        self.occ = self.color_occ[Color.WHITE] | self.color_occ[Color.BLACK]
        self.format_board.update_board(self.piece_bb)
        self.legal_moves = self.find_moves()
        self.format_board.update_legal_moves(self.legal_moves)
        print(self.format_board.get_legal_moves())

    def get_format_board(self):
        return self.format_board.get_board()

    def get_format_legal_moves(self):
        return self.format_board.get_legal_moves()

    def find_moves(self):
        a = self.move_generator.generate_pseudo_legal_moves(self)
        print("define", a)
        return a

    def get_piece_bb(self, piece, color=None):
        if color is None:
            color = self.color
        return self.piece_bb[color][piece]

    def make_move(self, move):
        print(self.legal_moves)

if __name__ == "__main__":
    b = Board()
    b.initialise_boards()
    b.find_moves()