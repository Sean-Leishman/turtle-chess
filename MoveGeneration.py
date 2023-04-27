import math
from copy import deepcopy, copy

import numpy as np

from Constants import *
from Bitboard import *
from Move import Move, Castle

import time

from TranspositionTable import TranspositionTable


class MoveGenerator():
    def __init__(self):
        self.tables = MoveGenerationTable()
        self.transpose_table = TranspositionTable()

        self.timings = {"genpseudo":[],"seperate":[],"king_attack1":[],"king_attack2":[], "checks":[],
                        "applymove":[],"piece_bb":[],"setboard":[]}

    def get_pawn_moves(self, src, board):
        normals, attacks = self.tables.pawn_moves[board.color]

        shifted_attacks = (board.color_occ[~board.color] & board.en_passant_mask[~board.color]) << np.uint8(8) if board.color == Color.WHITE else (board.color_occ[~board.color] & board.en_passant_mask[~board.color]) >> np.uint8(8)
        attack_moves = attacks[src] & board.color_occ[~board.color]
        en_passant_attacks = attacks[src] & shifted_attacks

        space_ahead_free = to_bitboard(src+8) & board.occ == EMPTY_BB if board.color == Color.WHITE else to_bitboard(src-8) & board.occ == EMPTY_BB
        if space_ahead_free:
            normals = normals[src] & ~board.occ
        else:
            normals = np.uint8(0)
        return attack_moves | normals, en_passant_attacks

    def get_knight_moves(self, src, board):
        return self.tables.knight_moves[src] & ~board.color_occ[board.color]

    def get_king_moves(self, src, board):
        return (self.tables.king_moves[src] & ~board.color_occ[board.color])

    def get_castling_moves(self, src, board):
        return self.generate_castling_moves(src, board)
    def generate_castling_moves(self,src,board):
        source = np.uint64(to_bitboard(src))

        if src == 4:
            king_moves = np.uint64(0)
            rook_original_pos = np.uint64(0)
            rook_moves = np.uint64(0)
            for side in Castling:
                t = self.tables.castling_moves[Color.WHITE][side] ^ self.tables.castling_masks[Color.WHITE][side]
                occupation = ~board.occ & self.tables.castling_masks[Color.WHITE][side]
                moved = board.has_moved & self.tables.castling_moves[Color.WHITE][side]
                if occupation ^ moved == t:
                    king_moves += source >> np.uint8(2) if side == Castling.QUEENSIDE else source << np.uint8(2)
                    rook_original_pos += np.uint64(0x1) if side == Castling.QUEENSIDE else np.uint64(0x80)
                    rook_moves += source >> np.uint8(1) if side == Castling.QUEENSIDE else source << np.uint8(1)
        elif src == 60:
            king_moves = np.uint64(0)
            rook_original_pos = np.uint64(0)
            rook_moves = np.uint64(0)
            for side in Castling:
                t = self.tables.castling_moves[Color.BLACK][side] ^ self.tables.castling_masks[Color.BLACK][side]
                occupation = ~board.occ & self.tables.castling_masks[Color.BLACK][side]
                moved = board.has_moved & self.tables.castling_moves[Color.BLACK][side]
                if occupation ^ moved == t:
                    king_moves += source >> np.uint8(2) if side == Castling.QUEENSIDE else source << np.uint8(2)
                    rook_original_pos += np.uint64(0x100000000000000) if side == Castling.QUEENSIDE else np.uint64(0x8000000000000000)
                    rook_moves += source >> np.uint8(1) if side == Castling.QUEENSIDE else source << np.uint8(1)
        else:
            return None

        return king_moves, rook_original_pos, rook_moves

    def get_bishop_moves(self, src, board):
        return (self.tables.generate_diag_moves(src, board.occ) ^ self.tables.generate_anti_diag_moves(src, board.occ)) & ~board.color_occ[board.color]

    def get_rook_moves(self, src, board):
        return (self.tables.generate_sliding_rank_moves(src, board.occ) ^ self.tables.generate_sliding_file_moves(src, board.occ)) & ~board.color_occ[board.color]
    def get_queen_moves(self, src, board):
        return self.get_rook_moves(src, board) | self.get_bishop_moves(src, board)
    def generate_pseudo_legal_moves(self, board):
        legal_moves = []
        castling_moves = []
        for piece in Piece:
            piece_bb = board.get_piece_bb(piece)
            for src in get_occupied_squares(piece_bb):
                if piece == Piece.PAWN:
                    moveset, en_passant = self.get_pawn_moves(src, board)
                    for move in get_occupied_squares(en_passant):
                        legal_moves.append(Move(index_from=src, index_to=move, en_passant=True))


                elif piece == Piece.KNIGHT:
                    moveset = self.get_knight_moves(src, board)
                elif piece == Piece.KING:
                    moveset = self.get_king_moves(src, board)
                    castling_moveset = self.get_castling_moves(src, board)
                    if castling_moveset is not None:
                        for king_to, rook_from, rook_to in zip(get_occupied_squares(castling_moveset[0]), get_occupied_squares(castling_moveset[1]), get_occupied_squares(castling_moveset[2])):
                            legal_moves.append(Castle(king_index_from=int(src), king_index_to=int(king_to), rook_index_from=int(rook_from), rook_index_to=int(rook_to)))
                elif piece == Piece.ROOK:
                    moveset = self.get_rook_moves(src, board)
                elif piece == Piece.BISHOP:
                    moveset = self.get_bishop_moves(src, board)
                elif piece == Piece.QUEEN:
                    moveset = self.get_queen_moves(src, board)
                else:
                    moveset = []
                for move in get_occupied_squares(moveset):
                    if (to_bitboard(move) & board.color_occ[~board.color] == EMPTY_BB):
                        legal_moves.append(Move(index_from=src, index_to=move))
                    else:
                        legal_moves.append(Move(index_from=src, index_to=move, is_capture=True))


        end_time = time.process_time_ns()
        return legal_moves

    def generate_legal_moves_in_new_position(self, board):
        pseudo_legal_moves = self.generate_pseudo_legal_moves(board)
        normal_moves = [x for x in pseudo_legal_moves if not hasattr(x, "rook_move")]
        castling_moves = [x for x in pseudo_legal_moves if hasattr(x, "rook_move")]

        normal_moves = list(filter(lambda x: not self.king_is_attacked(board, x), normal_moves))
        castling_moves = list(filter(lambda x: self.king_is_attacked_while_castling(board, x), castling_moves))

        return normal_moves + castling_moves
    def generate_legal_moves(self, board):
        node = self.transpose_table[board]
        if node is not None:
            if node.legal_moves == [] or node.legal_moves is None:
                legal_moves = self.generate_legal_moves_in_new_position(board)
                node.update(legal_moves=legal_moves)
                return legal_moves
            else:
                return node.legal_moves
        else:
            legal_moves = self.generate_legal_moves_in_new_position(board)
            self.transpose_table.put(board, math.inf, legal_moves)
            return legal_moves



    def king_is_attacked_while_castling(self, board, move):
        id = int(move.index_from + (move.king_move.index_to - move.king_move.index_from) // 2)
        inter_move = Move(index_from=move.index_from, index_to=id)

        if self.king_is_attacked(board, Move(index_from=0, index_to=0)):
            return False

        if self.king_is_attacked(board, inter_move):
            return False

        if self.king_is_attacked(board, move.king_move):
            return False

        return True

    def king_is_attacked_with_move(self, board, move):
        piece_bb = np.copy(board.piece_bb)
        color = copy(board.color)
        has_castled = copy(board.is_castled)

        mm_s = time.process_time_ns()
        board = board.apply_move(move, flexible=True, color=board.color)
        mm_e = time.process_time_ns()
        self.timings['applymove'].append(mm_e - mm_s)

        king_bb = board.get_piece_bb(Piece.KING)
        king_pos = get_occupied_squares(king_bb)

        opp_color = ~board.color

        if len(king_pos) < 1:
            return True

        king_pos = king_pos[0]

        mm_s = time.process_time_ns()
        opp_pawns = board.get_piece_bb(Piece.PAWN, opp_color)
        opp_knights = board.get_piece_bb(Piece.KNIGHT, opp_color)
        opp_bishops = board.get_piece_bb(Piece.BISHOP, opp_color)
        opp_rooks = board.get_piece_bb(Piece.ROOK, opp_color)
        opp_queens = board.get_piece_bb(Piece.QUEEN, opp_color)
        mm_e = time.process_time_ns()
        self.timings['piece_bb'].append(mm_e - mm_s)

        mm_s = time.process_time_ns()
        pawn_check = (self.tables.pawn_moves[board.color][PawnMoveType.ATTACK][king_pos] & opp_pawns) != EMPTY_BB
        knight_check = (self.tables.knight_moves[king_pos] & opp_knights) != EMPTY_BB
        bishop_check = (self.get_bishop_moves(king_pos, board) & (opp_bishops | opp_queens)) != EMPTY_BB
        rook_check = (self.get_rook_moves(king_pos, board) & (opp_rooks | opp_queens)) != EMPTY_BB
        mm_e = time.process_time_ns()
        self.timings['checks'].append(mm_e - mm_s)

        mm_s = time.process_time_ns()
        board.set_board(piece_bb, has_castled, color)
        mm_e = time.process_time_ns()
        self.timings['setboard'].append(mm_e - mm_s)
        return pawn_check | knight_check | rook_check | bishop_check

    def king_is_attacked_without_move(self,board):
        king_bb = board.get_piece_bb(Piece.KING)
        king_pos = get_occupied_squares(king_bb)

        opp_color = ~board.color

        if len(king_pos) < 1:
            return True

        king_pos = king_pos[0]

        opp_pawns = board.get_piece_bb(Piece.PAWN, opp_color)
        opp_knights = board.get_piece_bb(Piece.KNIGHT, opp_color)
        opp_bishops = board.get_piece_bb(Piece.BISHOP, opp_color)
        opp_rooks = board.get_piece_bb(Piece.ROOK, opp_color)
        opp_queens = board.get_piece_bb(Piece.QUEEN, opp_color)

        pawn_check = (self.tables.pawn_moves[board.color][PawnMoveType.ATTACK][king_pos] & opp_pawns) != EMPTY_BB
        knight_check = (self.tables.knight_moves[king_pos] & opp_knights) != EMPTY_BB
        bishop_check = (self.get_bishop_moves(king_pos, board) & (opp_bishops | opp_queens)) != EMPTY_BB
        rook_check = (self.get_rook_moves(king_pos, board) & (opp_rooks | opp_queens)) != EMPTY_BB

        return pawn_check | knight_check | bishop_check | rook_check
    def king_is_attacked(self, board, move=None, color=None):
        if color is None:
            color = board.color

        if move is not None:
            return self.king_is_attacked_with_move(board,move)
        else:
            #board.color = ~board.color
            return self.king_is_attacked_without_move(board)

class MoveGenerationTable(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MoveGenerationTable, cls).__new__(cls)
        return cls.instance
    def __init__(self):
        self.clear_files = self.generate_clear_files()
        self.clear_ranks = self.generate_clear_ranks()
        self.a1_h8_diag = np.uint64(0x8040201008040201)
        self.h1_a8_antidiag = np.uint64(0x0102040810204080)

        self.rank_masks = self.generate_rank_masks()
        self.file_masks = self.generate_file_masks()
        self.diag_masks = self.generate_diag_masks()
        self.anti_diag_masks = self.generate_anti_diag_masks()
        # generate moves for each position on board for pawn, knight and king
        self.knight_moves = self.generate_knight_moves()
        self.pawn_moves = self.generate_pawn_moves()
        self.king_moves = self.generate_king_moves()
        self.castling_moves = self.generate_possible_castling_moves()
        self.castling_masks = self.generate_castling_masks()
        self.first_rank_moves = self.generate_first_rank_moves()

    def generate_clear_files(self):
        bb = np.zeros(8, dtype=np.uint64)
        bb[0] = 0x101010101010101
        for i in range(8):
            bb[i] = bb[0] << np.uint8(i)
        return bb

    def generate_clear_ranks(self):
        bb = np.zeros(8, dtype=np.uint64)
        bb[0] = np.uint64(0xFF)
        for i in range(8):
            bb[i] = bb[0] << np.uint8(8 * i)
        return bb

    def generate_knight_moves(self):
        bb = np.zeros(64, dtype=np.uint64)
        knight_pos = np.uint64(1)

        for i in range(64):
            knight_clip_file_a_b = knight_pos & ~self.clear_files[0] & ~self.clear_files[1]
            knight_clip_file_a = knight_pos & ~self.clear_files[0]
            knight_clip_file_g_h = knight_pos & ~self.clear_files[6] & ~self.clear_files[7]
            knight_clip_file_h = knight_pos & ~self.clear_files[7]

            wwn = knight_clip_file_a_b << np.uint8(6)
            wnn = knight_clip_file_a << np.uint8(15)
            een = knight_clip_file_g_h << np.uint8(10)
            enn = knight_clip_file_h << np.uint8(17)
            ees = knight_clip_file_g_h >> np.uint8(6)
            ess = knight_clip_file_h >> np.uint8(15)
            wws = knight_clip_file_a_b >> np.uint8(10)
            wss = knight_clip_file_a >> np.uint8(17)

            bb[i] = wwn | wnn | een | enn | wws | wss | ees | ess
            knight_pos = knight_pos << np.uint8(1)
        return bb

    def generate_pawn_moves(self):
        bb = np.zeros((2, 2, 64), dtype=np.uint64)
        for idx,color in enumerate(Color):
            bb[idx][PawnMoveType.NORMAL] = self.generate_normal_pawn_moves(color)
            bb[idx][PawnMoveType.ATTACK] = self.generate_attack_moves(color)
        return bb

    def generate_normal_pawn_moves(self, color):
        bb = np.zeros(64, dtype=np.uint64)
        pawn_loc = np.uint64(1)
        shift_fowards = lambda color,bb, i: bb << np.uint64(8*i) if color == Color.WHITE else bb >> np.uint64(8*i)
        rank_mask = lambda color, i: self.clear_ranks[i] if color == Color.WHITE else self.clear_ranks[7-i]
        for i in range(64):
            pawn_second_rank = pawn_loc & rank_mask(color, 1)
            shift_one = shift_fowards(color,pawn_loc, 1).astype(np.uint64)
            shift_two = shift_fowards(color, pawn_second_rank, 2).astype(np.uint64)
            bb[i] = (shift_one | shift_two).astype(np.uint64)
            pawn_loc = pawn_loc << np.uint8(1)
        return bb

    def generate_attack_moves(self, color):
        bb = np.zeros(64, dtype=np.uint64)
        pawn_loc = np.uint64(1)

        rank_mask = lambda color, i: self.clear_ranks[i] if color == Color.WHITE else self.clear_ranks[7 - i]

        shift_fowards_left = lambda color, bb, i: bb << np.uint64(7) if color == Color.WHITE else bb >> np.uint64(9)
        shift_fowards_right = lambda color, bb, i: bb << np.uint64(9) if color == Color.WHITE else bb >> np.uint64(7)

        for i in range(64):
            pawn_clip_file_a = pawn_loc & ~self.clear_files[File.A]
            pawn_clip_file_h = pawn_loc & ~self.clear_files[File.H]
            shift_left = shift_fowards_left(color, pawn_clip_file_a, 1).astype(np.uint64)
            shift_right = shift_fowards_right(color, pawn_clip_file_h, 1).astype(np.uint64)
            bb[i] = shift_left | shift_right
            pawn_loc = pawn_loc << np.uint8(1)
        return bb

    def generate_king_moves(self):
        bb = np.zeros(64, dtype=np.uint64)
        king_pos = np.uint64(1)
        for i in range(64):
            king_clip_file_h = king_pos & ~self.clear_files[7]
            king_clip_file_a = king_pos & ~self.clear_files[0]

            nw = king_clip_file_a << np.uint8(7)
            n = king_pos << np.uint8(8)
            ne = king_clip_file_h << np.uint8(9)
            e = king_clip_file_h << np.uint8(1)

            se = king_clip_file_h >> np.uint8(7)
            s = king_pos >> np.uint8(8)
            sw = king_clip_file_a >> np.uint8(9)
            w = king_clip_file_a >> np.uint8(1)
            bb[i] = nw | n | ne | e | se | s | sw | w

            king_pos = king_pos << np.uint8(1)
        return bb

    def generate_castling_masks(self):
        bb = np.zeros((2, 2), dtype=np.uint64)
        bb[Color.WHITE][Castling.QUEENSIDE] = np.uint64(0xc)
        bb[Color.WHITE][Castling.KINGSIDE] = np.uint64(0x60)

        bb[Color.BLACK][Castling.QUEENSIDE] = np.uint64(0xc00000000000000)
        bb[Color.BLACK][Castling.KINGSIDE] = np.uint64(0x6000000000000000)
        return bb

    def generate_possible_castling_moves(self):
        bb = np.zeros((2, 2), dtype=np.uint64)
        bb[Color.WHITE][Castling.QUEENSIDE] = np.uint64(0x11)
        bb[Color.WHITE][Castling.KINGSIDE] = np.uint64(0x90)

        bb[Color.BLACK][Castling.QUEENSIDE] = np.uint64(0X1100000000000000)
        bb[Color.BLACK][Castling.KINGSIDE] = np.uint64(0x9000000000000000)
        return bb
    def generate_first_rank_moves(self):
        first_rank_moves = np.zeros((8, 256), dtype=np.uint8)
        left_ray = lambda x: x - np.uint8(1)
        right_ray = lambda x: (~x) & ~(x - np.uint8(1))

        for i in range(8):
            for occ in range(256):
                x = np.uint8(1) << np.uint8(i)
                occ_bb = np.uint8(occ)

                left_attacks = left_ray(x)
                left_blockers = left_attacks & occ_bb
                if left_blockers != np.uint8(0):
                    leftmost = np.uint8(1) << msb_bitscan(np.uint64(left_blockers))
                    left_garbage = left_ray(leftmost)
                    left_attacks ^= left_garbage

                right_attacks = right_ray(x)
                right_blockers = right_attacks & occ

                if right_blockers != np.uint8(0):
                    rightmost = np.uint8(1) << lsb_bitscan(np.uint64(right_blockers))
                    right_garbage = right_ray(rightmost)
                    right_attacks ^= right_garbage

                first_rank_moves[i][occ] = left_attacks ^ right_attacks
        return first_rank_moves
    def generate_sliding_file_moves(self, i, occ):
        f = i & np.uint8(7)
        # Shift to A file
        occ = self.clear_files[File.A] & (occ >> f)
        # Map occupancy and index to first rank
        occ = (self.a1_h8_diag * occ) >> np.uint8(56)
        first_rank_index = (i ^ np.uint8(56)) >> np.uint8(3)
        # Lookup moveset and map back to H file
        occ = self.a1_h8_diag * self.first_rank_moves[first_rank_index][occ]
        # Isolate H file and shift back to original file
        return (self.clear_files[File.H] & occ) >> (f ^ np.uint8(7))

    def generate_sliding_rank_moves(self, i, occ):
        f = i & np.uint8(7)
        occ = self.rank_masks[i] & occ
        occ = (self.clear_files[File.A] * occ) >> np.uint8(56)
        occ = self.clear_files[File.A] * self.first_rank_moves[f][occ]
        return self.rank_masks[i] & occ

    def generate_diag_masks(self):
        diag_masks = np.zeros(64, dtype=np.uint64)
        for i in range(64):
            diag = 8 * (i & 7) - (i & 56)
            north = -diag & (diag >> 31)
            south = diag & (-diag >> 31)
            diag_masks[i] = (self.a1_h8_diag >> np.uint8(south)) << np.uint8(north)
        return diag_masks

    def generate_anti_diag_masks(self):
        anti_diag_masks = np.zeros(64, dtype=np.uint64)
        for i in range(64):
            diag = 56 - 8 * (i & 7) - (i & 56)
            north = -diag & (diag >> 31)
            south = diag & (-diag >> 31)
            anti_diag_masks[i] = (self.h1_a8_antidiag >> np.uint8(south)) << np.uint8(north)
        return anti_diag_masks
    def generate_diag_moves(self, i, occ):
        f = i & np.uint8(7)
        occ = self.diag_masks[i] & occ
        occ = (self.clear_files[File.A] * occ) >> np.uint8(56)
        occ = self.clear_files[File.A] * self.first_rank_moves[f][occ]
        return self.diag_masks[i] & occ

    def generate_anti_diag_moves(self,i,occ):
        f = i & np.uint8(7)
        occ = self.anti_diag_masks[i] & occ
        occ = (self.clear_files[File.A] * occ) >> np.uint8(56)
        occ = self.clear_files[File.A] * self.first_rank_moves[f][occ]
        return self.anti_diag_masks[i] & occ

    def generate_rank_masks(self):
        bb = np.zeros(64, dtype=np.uint64)
        for i in range(64):
            bb[i] = self.clear_ranks[i // 8]
        return bb

    def generate_file_masks(self):
        bb = np.zeros(64, dtype=np.uint64)
        for i in range(64):
            bb[i] = self.clear_files[i % 8]
        return bb


if __name__=="__main__":
    m = MoveGenerator()