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



class MoveGeneration():
    def __init__(self):
        self.clear_files = self.generate_clear_files()
        self.clear_ranks = self.generate_clear_ranks()
        self.a1_h8_diag = np.uint64(0x8040201008040201)
        self.h1_a8_antidiag = np.uint64(0x0102040810204080)
        self.diag_masks = self.generate_diag_masks()
        self.anti_diag_masks = self.generate_anti_diag_masks()
        # generate moves for each position on board for pawn, knight and king
        self.knight_moves = self.generate_knight_moves()
        self.pawn_moves = self.generate_pawn_moves()
        self.king_moves = self.generate_king_moves()
        self.first_rank_moves = self.generate_first_rank_moves()
    def generate_clear_files(self):
        bb = np.zeros(8, dtype=np.uint64)
        bb[0] = 0x101010101010101
        for i in range(8):
            bb[i] = bb[0] << np.uint8(i)
        return bb

    def generate_clear_ranks(self):
        bb = np.zeros(8, dtype=np.uint64)
        bb[0] = 0xFF
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
            pawn_clip_first_rank = pawn_loc & ~rank_mask(color, 0)
            pawn_second_rank = pawn_loc & rank_mask(color, 1)
            shift_one = shift_fowards(color,pawn_clip_first_rank, 1).astype(np.uint64)
            shift_two = shift_fowards(color, pawn_second_rank, 2).astype(np.uint64)
            bb[i] = (shift_one | shift_two).astype(np.uint64)
            pawn_loc = pawn_loc << np.uint8(1)
        return bb

    def generate_attack_moves(self, color):
        bb = np.zeros(64, dtype=np.uint64)
        pawn_loc = np.uint64(1)

        rank_mask = lambda color, i: self.clear_ranks[i] if color == Color.WHITE else self.clear_ranks[7 - i]

        shift_fowards_left = lambda color, bb, i: bb << np.uint64(7) if color == Color.WHITE else bb >> np.uint64(7)
        shift_fowards_right = lambda color, bb, i: bb << np.uint64(9) if color == Color.WHITE else bb >> np.uint64(9)

        for i in range(64):
            pawn_clip_file_a = pawn_loc & ~self.clear_files[0] & ~rank_mask(color, 0)
            pawn_clip_file_h = pawn_loc & ~self.clear_files[7] & ~rank_mask(color, 0)
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
        occ = self.clear_ranks[i] & occ
        occ = (self.clear_files[File.A] * occ) >> np.uint8(56)
        occ = self.clear_files[File.A] * self.first_rank_moves[f][occ]
        return self.clear_ranks[i] * occ

    def generate_diag_masks(self):
        diag_masks = np.zeros(8, dtype=np.uint64)
        for i in range(8):
            diag = 8 * (i & 7) - (i & 56)
            north = -diag & (diag >> 31)
            south = diag & (-diag >> 31)
            diag_masks[i] = (self.a1_h8_diag >> np.uint8(south)) << np.uint8(north)
        return diag_masks

    def generate_anti_diag_masks(self):
        anti_diag_masks = np.zeros(8, dtype=np.uint64)
        for i in range(8):
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

if __name__=="__main__":
    m = MoveGeneration().first_rank_moves
    print(m)