import math
from copy import deepcopy, copy

import time
from MoveGeneration import MoveGenerator
from Model import Model
from Bitboard import *
from Evaluation import Evaluation
from Move import Move
from TranspositionTable import TranspositionTable
from Zobrist import Zobrist, POLYGLOT_RANDOM_ARRAY
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
        self.timings = {"openings": [], "move": [], "mm": [], "movegen": [], "evaluator": [], "makemove": [], "setboard":[]}

        self.openings_book = Polyglot.open_reader("Perfect2017.bin")
        self.model_mode = False

        self.transpose_table = TranspositionTable()

        self.nodes = 0



    def find_best_move(self, board):
        self.nodes = 0
        max_score = -math.inf
        found_move = False
        moves = []
        if not self.model_mode:
            for entry in self.openings_book.find_all(board):
                moves.append(entry)
                found_move = True
            if found_move:
                return parse_move(moves[0].move)
            else:
                self.model_mode = False

        # Iterative Deepening Search
        current_depth = 0
        initial_depth = 0
        for d in range(1,3):
            current_depth = d + initial_depth
            next_move = self.init_minimax(board, current_depth)
        """
        print(self.timings)
        print(sum(self.timings["openings"])/len(self.timings['openings']))
        print(sum(self.timings["move"]) / len(self.timings['move']))
        print(sum(self.timings["mm"]) / len(self.timings['mm']) / 1e9)
        print(sum(self.timings["evaluator"]) / len(self.timings['evaluator']) / 1e9)
        print(sum(self.timings["movegen"]) / len(self.timings['movegen']) / 1e9)
        print(sum(self.timings["makemove"]) / len(self.timings['makemove']) / 1e9)
        print(sum(self.timings["setboard"]) / len(self.timings['setboard']) / 1e9)
        print("NODES", self.nodes)
        """
        self.transpose_table.clear()
        return next_move

    def order_moves(self, board, legal_moves):
        legal_moves = sorted(legal_moves, key=lambda x: x.is_capture, reverse=True)
        values = []

        for move in legal_moves:
            piece_bb = np.copy(board.piece_bb)
            has_castled = copy(board.is_castled)
            color = copy(board.color)

            board.apply_move(move)
            ttnode = self.transpose_table[board]
            if ttnode is not None and ttnode.value != math.inf and ttnode.value is not None:
                values.append(ttnode.value)
            else:
                values.append(0)
            board.set_board(piece_bb, has_castled, color)

        return [x for _, x in sorted(zip(values, legal_moves), key=lambda x: x[0], reverse=True)]

    def init_minimax(self, board, current_depth):
        legal_moves = self.move_generator.generate_legal_moves(board)
        legal_moves = self.order_moves(board, legal_moves)

        bestVal = -math.inf
        bestMove = None
        for move in legal_moves:
            piece_bb = np.copy(board.piece_bb)
            has_castled = copy(board.is_castled)
            color = copy(board.color)
            node = board.apply_move(move)

            self.nodes += 1

            score = self.minimax(node, 1, current_depth, False, -math.inf, math.inf)
            node.set_board(piece_bb, has_castled, color)

            if score > bestVal:
                bestVal = score
                bestMove = move
        return bestMove

    def minimax(self, node, curr_depth, max_depth, isMaximisingPlayer, alpha, beta):
        legal_moves = self.move_generator.generate_legal_moves(node)
        legal_moves = self.order_moves(node, legal_moves)

        if curr_depth == max_depth:
            #score = self.model.predict_scores(convert_to_ml_boards(node))
            score = -self.evaluator.evaluate(node)
            ttnode = self.transpose_table[node]

            if ttnode is not None:
                if ttnode.value < score or ttnode.value == math.inf:
                    ttnode.update(value=score)
            else:
                self.transpose_table.put(node, score)
            return score

        if isMaximisingPlayer:
            bestVal = -math.inf

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

            for move in legal_moves:
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

