from copy import deepcopy

from Constants import *
from GUI import GUI
import pygame, sys
from Move import Move
from Board import Board
from Bitboard import *
from Search import Search
import math

def get_coord(pos):
    cord = [0] * 2
    for i in range(len(pos)):
        cord[i] = math.floor(pos[i] / SQUARE_SIZE)
    return cord

def parse_move(move):
    return Move(index_from=move.from_square, index_to=move.to_square)

class Game():
    def __init__(self):
        pygame.init()
        self.board = Board()
        self.game_type = GameType.COMPUTER

        self.is_piece_selected = False
        self.selected_piece = None
        self.move = Move()
        self.gui = GUI()
        self.search = Search()

    def play(self):
        if self.game_type == GameType.COMPUTER:
            self.play_computer()
        else:
            self.play_user()
    def play_computer(self):
        user_color = Color.WHITE
        self.board.initialise_boards()

        while self.board.game_state == GameState.NORMAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.board.color != user_color:
                    move = self.search.find_best_move(deepcopy(self.board)).move
                    self.board.make_move(parse_move(move))

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not self.is_piece_selected and self.board.game_state == GameState.NORMAL:
                        self.move.set_coord_from(get_coord(pos))
                        if self.board.get_format_board()[self.move.coord_from[0]][self.move.coord_from[1]] != None:
                            self.is_piece_selected = True
                    elif self.is_piece_selected:
                        self.move.set_coord_to(get_coord(pos))
                        print("Make Move")
                        self.board = self.board.make_move(self.move)
                        print("Move Made")
                        self.is_piece_selected = False
                        move = self.search.find_best_move(deepcopy(self.board))
                        print(move)
                    else:
                        break
            if self.is_piece_selected:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves(), self.move)
            else:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves())
        self.board = Board()
        self.board.initialise_boards()
        self.play_computer()
    def play_user(self):
        self.board.initialise_boards()
        while self.board.game_state == GameState.NORMAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not self.is_piece_selected and self.board.game_state == GameState.NORMAL:
                        self.move.set_coord_from(get_coord(pos))
                        if self.board.get_format_board()[self.move.coord_from[0]][self.move.coord_from[1]] != None:
                            self.is_piece_selected = True
                    elif self.is_piece_selected:
                        self.move.set_coord_to(get_coord(pos))
                        print("Make Move")
                        self.board = self.board.make_move(self.move)
                        print("Move Made")
                        self.is_piece_selected = False
                        move = self.search.find_best_move(deepcopy(self.board))
                        print(move)
                    else:
                        break
            if self.is_piece_selected:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves(), self.move)
            else:
                self.gui.draw_window(self.board.get_format_board(), self.board.get_format_legal_moves())
        self.board = Board()
        self.board.initialise_boards()
        self.play_user()

if __name__ == "__main__":
    game = Game()
    game.play()
