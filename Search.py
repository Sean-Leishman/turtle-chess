import math
from copy import deepcopy

from MoveGeneration import MoveGenerator
from Model import Model
from Bitboard import *
import Polyglot

COLOR_CONVERT = {
    -1: -1,
    0: 1,
    1: -1,
}
def convert_to_ml_boards(node):
    fields = np.zeros((8,8,7))
    for piece in Piece:
        for color in Color:
            for src in get_occupied_squares(node.piece_bb[color][piece]):
                row, col = convert_index_to_row_col(src)
                fields[row][col][piece] = COLOR_CONVERT[color]
    return np.array([fields])


class Search():
    def __init__(self):
        self.move_generator = MoveGenerator()
        self.model = Model()

    def find_best_move(self, board):
        max_score = 0
        found_move = False
        moves = []
        with Polyglot.open_reader("Perfect2017.bin") as reader:
            for entry in reader.find_all(board):
                print(entry.move, entry.weight)
                moves.append(entry)
                found_move = True
        if not found_move:
            for move in self.move_generator.generate_legal_moves(board):
                node = board.make_move(move)
                score = self.minimax(node, 1, 2, True, -math.inf, math.inf)
                if score > max_score:
                    max_score = score
                    best_move = move
        return moves[0]

    def minimax(self, node, curr_depth, max_depth, isMaximisingPlayer, alpha, beta):
        if curr_depth == max_depth:
            score = self.model.predict_scores(convert_to_ml_boards(node))
            print(score)
            return score[0][0]
        if isMaximisingPlayer:
            bestVal = -math.inf
            for move in self.move_generator.generate_legal_moves(node):
                node.make_move(move)
                value = self.minimax(deepcopy(node), curr_depth+1, max_depth, not isMaximisingPlayer, alpha, beta)
                bestVal = max(bestVal, value)
                alpha = max(bestVal, alpha)
                if beta <= alpha:
                    break
            return bestVal

        else:
            bestVal = math.inf
            for move in self.move_generator.generate_legal_moves(node):
                node.make_move(move)
                value = self.minimax(deepcopy(node), curr_depth + 1, max_depth, not isMaximisingPlayer, alpha, beta)
                bestVal = min(bestVal, value)
                beta = min(bestVal, beta)
                if beta <= alpha:
                    break
            return bestVal
