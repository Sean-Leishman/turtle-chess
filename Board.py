import time

import numpy as np
from Constants import *
from MoveGeneration import MoveGenerator
from Bitboard import *
from Move import Move
import copy

class FormattedBoard():
    def __init__(self):
        self.board = [[None] * 8 for i in range(8)]
        self.legal_moves = [[[] for j in range(8)] for i in range(8)]

    def get_board(self):
        return self.board

    def update_board(self, bb, king_in_check):
        self.board = [[None] * 8 for i in range(8)]
        for color in Color:
            for piece in Piece:
                for src in get_occupied_squares(bb[color][piece]):
                    row, col = convert_index_to_row_col(src)
                    if piece == piece.KING:
                        if color in king_in_check and king_in_check[color]:
                            self.board[row][col] = (color, piece, True)
                        elif color == Color.BLACK and -1 in king_in_check and king_in_check[-1]:
                            self.board[row][col] = (color, piece, True)
                        else:
                            self.board[row][col] = (color, piece, False)
                    else:
                        self.board[row][col] = (color, piece, False)

    def get_legal_moves(self):
        return self.legal_moves

    def update_legal_moves(self, bbs):
        self.legal_moves = [[[] for j in range(8)] for i in range(8)]
        for idx, move in enumerate(bbs):
            row_from, col_from = convert_index_to_row_col(move.index_from)
            row_to, col_to = convert_index_to_row_col(move.index_to)
            self.legal_moves[row_from][col_from].append((row_to, col_to))


class Board():
    def __init__(self):
        self.piece_bb = np.zeros((2, 6), dtype=np.uint64)
        self.color_occ = np.zeros(2, dtype=np.uint64)
        self.occ = np.zeros(1, dtype=np.uint64)

        self.has_moved = np.uint64(0x9100000000000091)

        self.move_generator = MoveGenerator()
        self.color = Color.WHITE

        self.format_board = FormattedBoard()
        self.legal_moves = None

        # {WHITE: 0, BLACK: -1}
        self.king_in_check = {0: False, -1: False}



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
        self.format_board.update_board(self.piece_bb, self.king_in_check)
        self.legal_moves = self.find_moves()
        self.format_board.update_legal_moves(self.legal_moves)

    def get_format_board(self):
        return self.format_board.get_board()

    def get_format_legal_moves(self):
        return self.format_board.get_legal_moves()

    def find_moves(self):
        a = self.move_generator.generate_legal_moves(self)
        return a

    def get_piece_bb(self, piece, color=None):
        if color is None:
            color = self.color
        return self.piece_bb[color][piece]

    def get_piece_on(self, sq):
        for color in Color:
            for piece in Piece:
                if is_set(sq, self.piece_bb[color][piece]):
                    return piece
        return None

    def set_square(self, sq, piece, color=None):
        if color is None:
            color = self.color

        piece_bb = self.get_piece_bb(piece)
        color_bb = self.color_occ[color]
        all_bb = self.occ

        self.piece_bb[color][piece] = set_square(sq, piece_bb)
        self.color_occ[color] = set_square(sq, color_bb)
        self.occ = set_square(sq, all_bb)

    def clear_square(self, sq, color=None):
        if color is None:
            color = self.color

        piece = self.get_piece_on(sq)
        if piece is None:
            return

        piece_bb = self.get_piece_bb(piece, color)
        color_occ = self.color_occ[color]
        all_occ = self.occ

        self.piece_bb[color][piece] = clear_square(sq, piece_bb)
        self.color_occ[color] = clear_square(sq, color_occ)
        self.occ = clear_square(sq, all_occ)

    def make_move(self, move, inplace=True):
        if not inplace:
            newBoard = Board()
            newBoard.pieces = np.copy(self.piece_bb)
            newBoard.color_occ = np.copy(self.color_occ)
            newBoard.occ = np.copy(self.occ)
            newBoard.color = self.color
            newBoard.legal_moves = np.copy(self.legal_moves)

        else:
            newBoard = self

        move_exists_in_legal_moves = any(
            map(lambda x: x.index_from == move.index_from and x.index_to == move.index_to, newBoard.legal_moves))

        if not move_exists_in_legal_moves:
            return newBoard

        piece = newBoard.get_piece_on(move.index_from)

        if piece == piece.KING:
            if abs(move.index_from - move.index_to) == 2:
                # Castling
                move = list(filter(lambda x: x.index_from == move.index_from and x.index_to == move.index_to,
                            newBoard.legal_moves))[0]
                newBoard.clear_square(move.rook_move.index_from)
                newBoard.set_square(move.rook_move.index_to, piece.ROOK)

                newBoard.has_moved = ~np.uint64(to_bitboard(move.rook_move.index_from)) & newBoard.has_moved

        newBoard.has_moved = ~np.uint64(to_bitboard(move.index_from)) & newBoard.has_moved

        newBoard.clear_square(move.index_from)
        newBoard.clear_square(move.index_to, ~newBoard.color)
        newBoard.set_square(move.index_to, piece)

        newBoard.color = ~newBoard.color

        copyBoard = copy.deepcopy(newBoard)
        copyBoard.color = ~copyBoard.color

        newBoard.king_in_check[newBoard.color] = newBoard.move_generator.king_is_attacked(copyBoard)
        newBoard.king_in_check[~newBoard.color] = False
        print(newBoard.king_in_check)
        newBoard.legal_moves = newBoard.find_moves()
        newBoard.format_board.update_board(newBoard.piece_bb, newBoard.king_in_check)
        newBoard.format_board.update_legal_moves(newBoard.legal_moves)

        return newBoard

    def apply_move(self, move):
        piece = self.get_piece_on(move.index_from)

        if piece == piece.KING:
            if abs(move.index_from - move.index_to) == 2:
                # Castling
                move = list(filter(lambda x: x.index_from == move.index_from and x.index_to == move.index_to,self.legal_moves))
                if len(move) == 0:
                    return self
                self.clear_square(move.rook_move.index_from)
                self.set_square(move.rook_move.index_to, piece.ROOK)
                #self.has_moved = ~move.rook_move.index_from & ~move.index_from & self.has_moved

        self.clear_square(move.index_from)
        self.clear_square(move.index_to, ~self.color)
        self.set_square(move.index_to, piece)

        self.color = ~self.color
        return self

if __name__ == "__main__":
    b = Board()
    b.initialise_boards()
    b.find_moves()
