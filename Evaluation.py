import math
import numpy as np

from enum import IntEnum

from Board import Board
from Constants import Color, Piece
from Bitboard import *
from MoveGeneration import MoveGenerator


CENTER = np.uint64(0x3c3c3c3c0000)

class Score(IntEnum):
    PAWN = np.int32(100)
    KNIGHT = np.int32(300)
    BISHOP = np.int32(300)
    ROOK = np.int32(500)
    QUEEN = np.int32(900)
    CHECKMATE = np.int32(-1000000)
    CASTLED = np.int32(1000000000)
    CENTER = np.int32(5)
    MOVE = np.int32(5)

class Evaluation():
    def __init__(self, color=Color.BLACK):
        self.score = -math.inf
        self.move_generator = MoveGenerator()
        self.color = color

    def evaluate(self, board: Board):
        if self.color == Color.WHITE:
            return self.eval_pieces(board) + self.eval_center(board) #+ self.eval_moves(board) + self.eval_castled(board)
        else:
            return -1 * (self.eval_pieces(board) + self.eval_center(board)) #+ self.eval_moves(board) + self.eval_castled(board)

    def piece_diff(self, board: Board, piece: Piece):
        return np.int32(pop_count(board.piece_bb[board.color][piece])) - np.int32(
            pop_count(board.piece_bb[~board.color][piece]))

    def eval_pieces(self, board: Board):
        return (Score.PAWN.value * self.piece_diff(board, Piece.PAWN)
                + Score.KNIGHT.value * self.piece_diff(board, Piece.KNIGHT)
                + Score.BISHOP.value * self.piece_diff(board, Piece.BISHOP)
                + Score.ROOK.value * self.piece_diff(board, Piece.ROOK)
                + Score.QUEEN.value * self.piece_diff(board, Piece.QUEEN))

    def eval_center(self, board: Board):
        return Score.CENTER.value * pop_count(board.color_occ[board.color] & CENTER)

    def eval_moves(self, board: Board):
        num = len(list(self.move_generator.generate_legal_moves(board)))
        if num == 0:
            return Score.CHECKMATE.value
        else:
            return Score.MOVE.value * np.int32(num)

    def eval_castled(self, board: Board):
        if board.is_castled[board.color]:
            return Score.CASTLED.value
        return 0