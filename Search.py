import math
from copy import deepcopy, copy

import time
from MoveGeneration import MoveGenerator
from Model import Model
from Bitboard import *
from Evaluation import Evaluation
from Move import Move
import Polyglot
from memory_profiler import profile


# instantiating the decorator


def parse_move(move):
    return Move(index_from=move.from_square, index_to=move.to_square)

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
        self.evaluator = Evaluation()
        self.timings = {"openings": [], "move": [], "mm": []}

        self.nodes = 0

    def find_best_move(self, board):
        max_score = -math.inf
        found_move = False
        moves = []
        op_time = time.process_time_ns()
        with Polyglot.open_reader("Perfect2017.bin") as reader:
            for entry in reader.find_all(board):
                moves.append(entry)
                found_move = True
            if found_move:
                return parse_move(moves[0].move)

        op_end = time.process_time_ns()
        self.timings["openings"].append(op_end-op_time)

        if board.legal_moves == []:
            print("CHECKMATE")
        print(board.legal_moves)
        for move in board.legal_moves:
            if hasattr(move, "rook_move"):
                print("yes")

            am_s = time.process_time_ns()

            piece_bb = np.copy(board.piece_bb)
            has_castled = copy(board.is_castled)
            color = copy(board.color)

            node = board.apply_move(move)
            am_e = time.process_time_ns()
            self.timings["move"].append(am_e - am_s)

            self.nodes += 1

            mm_s = time.process_time_ns()
            score = self.minimax(node, 1, 3, False, -math.inf, math.inf)
            node.set_board(piece_bb, has_castled, color)
            mm_e = time.process_time_ns()
            self.timings["mm"].append(mm_e - mm_s)

            if score > max_score:
                max_score = score
                best_move = move

        print(self.timings)
        print(sum(self.timings["openings"])/len(self.timings['openings']))
        print(sum(self.timings["move"]) / len(self.timings['move']))
        print(sum(self.timings["mm"]) / len(self.timings['mm']))
        print("NODES", self.nodes)

        return best_move

    def minimax(self, node, curr_depth, max_depth, isMaximisingPlayer, alpha, beta):
        if curr_depth == max_depth:
            #score = self.model.predict_scores(convert_to_ml_boards(node))
            score = self.evaluator.evaluate(node)
            return score
        if isMaximisingPlayer:
            bestVal = -math.inf

            legal_moves = self.move_generator.generate_legal_moves(node)
            for move in legal_moves:
                piece_bb = np.copy(node.piece_bb)
                has_castled = copy(node.is_castled)
                color = copy(node.color)

                node.apply_move(move)

                self.nodes += 1
                value = self.minimax(node, curr_depth+1, max_depth, not isMaximisingPlayer, alpha, beta)
                node.set_board(piece_bb, has_castled, color)
                bestVal = max(bestVal, value)
                alpha = max(bestVal, alpha)
                if beta <= alpha:
                    break
            return bestVal

        else:
            bestVal = math.inf
            for move in self.move_generator.generate_legal_moves(node):
                piece_bb = np.copy(node.piece_bb)
                has_castled = copy(node.is_castled)
                color = copy(node.color)

                node.apply_move(move)
                self.nodes += 1
                value = self.minimax(node, curr_depth + 1, max_depth, not isMaximisingPlayer, alpha, beta)
                node.set_board(piece_bb, has_castled, color)
                bestVal = min(bestVal, value)
                beta = min(bestVal, beta)
                if beta <= alpha:
                    break
            return bestVal
