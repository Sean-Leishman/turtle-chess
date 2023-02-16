
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
                        if self.board.get_format_board()[self.move.coord_from[0]][self.move.coord_from[1]] != None:
                            self.is_piece_selected = True
                    elif self.is_piece_selected:
                        self.move.set_coord_to(get_coord(pos))
                        print("Make Move")
                        self.board = self.board.make_move(self.move)
                        print("Move Made")
                        self.is_piece_selected = False
            if self.is_piece_selected:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves(), self.move)
            else:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves())

if __name__ == "__main__":
    Game().play()
