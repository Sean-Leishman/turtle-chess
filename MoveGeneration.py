import numpy as np
from Constants import *

class MoveGeneration():
    def __init__(self):
        self.clear_files = self.generate_clear_files()
        self.clear_ranks = self.generate_clear_ranks()
        # generate moves for each position on board for pawn, knight and king
        self.knight_moves = self.generate_knight_moves()
        self.pawn_moves = self.generate_pawn_moves()
        self.king_moves = self.generate_king_moves()

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

if __name__=="__main__":
    m = MoveGeneration().pawn_moves
    print(m[Color.BLACK][PawnMoveType.ATTACK])