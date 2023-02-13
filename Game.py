
from Constants import *
from GUI import GUI
import pygame, sys
from Move import Move
from Board import Board
from Bitboard import *
import math

def get_coord(pos):
    cord = [0] * 2
    for i in range(len(pos)):
        cord[i] = math.floor(pos[i] / SQUARE_SIZE)
    return cord

class Move():
    def __init__(self):
        self.coord_from = None
        self.coord_to = None

        self.index_to = None
        self.index_from = None

    def set_coord_from(self, coord):
        self.coord_from = coord
        self.index_from = convert_row_col_to_index(*coord)

    def set_coord_to(self, coord):
        self.coord_to = coord
        self.index_to = convert_row_col_to_index(*coord)

class Game():
    def __init__(self):
        pygame.init()
        self.board = Board()

        self.is_piece_selected = False
        self.selected_piece = None
        self.move = Move()
        self.gui = GUI()

    def play(self):
        self.board.initialise_boards()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not self.is_piece_selected:
                        self.move.set_coord_from(get_coord(pos))
                        self.is_piece_selected = True
                    elif self.is_piece_selected:
                        self.move.set_coord_to(get_coord(pos))
                        self.board.make_move(self.move)
                        self.is_piece_selected = False
            if self.is_piece_selected:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves(), self.move)
            else:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves())

if __name__ == "__main__":
    Game().play()
