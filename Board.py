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
        self.last_move = None

    def get_board(self):
        return self.board

    def __str__(self):
        string = ""
        for i in range(len(self.board) - 1, -1, -1):
            string += "----------------------------\n"
            for j in range(len(self.board[i])):
                if self.board[i][j] is not None and Color(self.board[i][j][0]) == Color.WHITE:
                    string += f"| {Piece(self.board[i][j][1]).name[0]} "
                elif self.board[i][j] is not None:
                    string += f"| {Piece(self.board[i][j][1]).name[0].lower()} "
                else:
                    string += "|   "
            string += "|\n"
        string += "------------------------------\n"
        return string

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

    def update_last_move(self, last_move):
        self.last_move = last_move

    def get_last_move(self):
        return self.last_move


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
        self.is_castled = {0: False, -1: False}


        self.en_passant_mask = np.zeros(2, dtype=np.uint64)

        self.game_state = GameState.NORMAL

        self.history = []

        self.fb = FormattedBoard()

    def __str__(self):
        self.fb.update_board(self.piece_bb, self.king_in_check)
        return str(self.fb)

    def set_board(self, piece_bb, is_castled, color):
        self.piece_bb = piece_bb
        self.color_occ = self.color_occ & EMPTY_BB
        for p in Piece:
            for c in Color:
                self.color_occ[c] |= self.piece_bb[c][p]

        self.occ = self.color_occ[Color.WHITE] | self.color_occ[Color.BLACK]
        self.is_castled = is_castled
        self.color = color

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

    def has_kingside_castling_rights(self, color):
        if color == Color.WHITE:
            return ((np.uint64(0x90) & self.has_moved) ^ np.uint64(0x90)) == EMPTY_BB
        elif color == Color.BLACK:
            return ((np.uint64(0x9000000000000000) & self.has_moved) ^ np.uint64(0x9000000000000000)) == EMPTY_BB

    def has_queenside_castling_rights(self, color):
        if color == Color.WHITE:
            return ((np.uint64(0x11) & self.has_moved) ^ np.uint64(0x11)) == EMPTY_BB
        elif color == Color.BLACK:
            return ((np.uint64(0x1100000000000000) & self.has_moved) ^ np.uint64(0x1100000000000000)) == EMPTY_BB

    def get_format_board(self):
        return self.format_board

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

        piece_bb = self.piece_bb[color][piece]
        color_bb = self.color_occ[color]
        all_bb = self.occ

        self.piece_bb[color][piece] = set_square(sq, piece_bb)
        self.color_occ[color] = set_square(sq, color_bb)
        self.occ = set_square(sq, all_bb)

    def clear_square(self, sq, piece=None,color=None):
        if color is None:
            color = self.color

        if piece is None:
            piece = self.get_piece_on(sq)
            if piece is None:
                return

        piece_bb = self.piece_bb[color][piece]
        color_occ = self.color_occ[color]
        all_occ = self.occ

        self.piece_bb[color][piece] = clear_square(sq, piece_bb)
        self.color_occ[color] = clear_square(sq, color_occ)
        self.occ = clear_square(sq, all_occ)

    def is_end_of_game(self):
        if len(self.legal_moves) == 0 and self.king_in_check[self.color]:
            return GameState.CHECKMATE
        elif len(self.legal_moves) == 0 and not self.king_in_check[self.color]:
            return GameState.STALEMATE
        else:
            return GameState.NORMAL
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
        try:
            newBoard.en_passant_mask[~newBoard.color] = EMPTY_BB
        except:
            pass

        if piece == piece.KING:
            if abs(move.index_from - move.index_to) == 2:
                # Castling
                move = list(filter(lambda x: x.index_from == move.index_from and x.index_to == move.index_to,
                            newBoard.legal_moves))[0]
                newBoard.clear_square(move.rook_move.index_from)
                newBoard.set_square(move.rook_move.index_to, piece.ROOK)
                newBoard.has_moved = ~np.uint64(to_bitboard(move.rook_move.index_from)) & newBoard.has_moved
                newBoard.is_castled[newBoard.color] = True
        elif piece == piece.PAWN:
            white_promote = to_bitboard(move.index_from) & newBoard.move_generator.tables.clear_ranks[
                Rank.SEVEN] != EMPTY_BB
            black_promote = to_bitboard(move.index_from) & newBoard.move_generator.tables.clear_ranks[Rank.TWO] != EMPTY_BB
            if abs(move.index_from - move.index_to) == 16:
                newBoard.en_passant_mask[newBoard.color] = to_bitboard(move.index_to)
            elif move.index_from // 8 == 4 or move.index_from // 8 == 5:
                move = list(filter(lambda x: x.index_from == move.index_from and x.index_to == move.index_to,
                                   newBoard.legal_moves))[0]
                if move.en_passant:
                    newBoard.clear_square(move.index_to - 8 if newBoard.color == Color.WHITE else move.index_to + 8, ~newBoard.color)
            elif (newBoard.color == Color.WHITE and white_promote) or (newBoard.color != Color.WHITE and black_promote):
                piece = Piece.QUEEN


        newBoard.has_moved = ~np.uint64(to_bitboard(move.index_from)) & newBoard.has_moved

        newBoard.clear_square(move.index_from)
        newBoard.clear_square(move.index_to, color=~newBoard.color)
        newBoard.set_square(move.index_to, piece)

        newBoard.color = ~newBoard.color

        piece_bb = np.copy(newBoard.piece_bb)
        has_castled = copy.copy(newBoard.is_castled)
        color = copy.copy(newBoard.color)

        newBoard.king_in_check[newBoard.color] = newBoard.move_generator.king_is_attacked(newBoard)
        newBoard.set_board(piece_bb, has_castled, color)
        newBoard.king_in_check[~newBoard.color] = False
        newBoard.legal_moves = newBoard.find_moves()
        newBoard.game_state = newBoard.is_end_of_game()

        newBoard.history.append(copy.deepcopy(move))
        newBoard.format_board.update_board(newBoard.piece_bb, newBoard.king_in_check)
        newBoard.format_board.update_legal_moves(newBoard.legal_moves)
        newBoard.format_board.update_last_move(newBoard.history[-1])
        print("LAST", newBoard.format_board.get_last_move())
        return newBoard

    def apply_move(self, move, flexible=False, color=None):

        piece = self.get_piece_on(move.index_from)
        if piece == None:
            return self

        if piece == piece.KING:
            if not flexible and abs(move.index_from - move.index_to) == 2:
                # Castling
                #move = list(filter(lambda x: x.index_from == move.index_from and x.index_to == move.index_to,self.legal_moves))
                if move is not None:
                    self.clear_square(move.rook_move.index_from)
                    self.set_square(move.rook_move.index_to, piece.ROOK)
                    self.has_moved = ~np.uint64(to_bitboard(move.rook_move.index_from)) & self.has_moved
                    self.is_castled[self.color] = True
                else:
                    return self
        elif piece == piece.PAWN:
            """
            white_promote = to_bitboard(move.index_from) & self.move_generator.tables.clear_ranks[
                Rank.SEVEN] != EMPTY_BB
            black_promote = to_bitboard(move.index_from) & self.move_generator.tables.clear_ranks[Rank.TWO] != EMPTY_BB
            if abs(move.index_from - move.index_to) == 16:
                self.en_passant_mask[self.color] = to_bitboard(move.index_to)
            elif move.index_from // 8 == 4 or move.index_from // 8 == 5:
                if move.en_passant:
                    self.clear_square(move.index_to - 8 if self.color == Color.WHITE else move.index_to + 8, ~self.color)
            elif (self.color == Color.WHITE and white_promote) or (self.color != Color.WHITE and black_promote):
                piece = Piece.QUEEN
            """

        self.clear_square(move.index_from, piece, self.color)
        self.clear_square(move.index_to, color=~self.color)
        self.set_square(move.index_to, piece)

        if not flexible:
            self.color = ~self.color
        return self

if __name__ == "__main__":
    b = Board()
    b.initialise_boards()
    b.find_moves()
