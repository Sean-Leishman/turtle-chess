from copy import deepcopy

from Constants import *
from GUI import GUI
import pygame, sys
from Move import Move
from Board import Board
from Bitboard import *
from Search import Search
import math

coord_offset = lambda x: (3.5 - x) * 2

def get_coord(pos):
    print(pos)
    coord = [0] * 2
    coord[0] = math.floor(pos[1] / SQUARE_SIZE)
    coord[0] = int(coord[0] + coord_offset(coord[0]))
    coord[1] = math.floor(pos[0] / SQUARE_SIZE)
    return coord

class Game():
    def __init__(self):
        pygame.init()
        self.board = Board()
        self.game_type = GameType.USER

        self.is_piece_selected = False
        self.selected_piece = None
        self.move = Move()
        self.gui = GUI()
        self.search = Search()

    def play(self):
        if self.game_type == GameType.COMPUTER:
            self.play_computer()
        elif self.game_type == GameType.SIMULATION:
            self.simulate_game()
        else:
            self.play_user()

    def simulate_game(self):
        self.board.initialise_boards()
        finding_move = False

        while self.board.game_state == GameState.NORMAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.gui.draw_window(self.board.get_format_board())
            if not finding_move:
                finding_move = True
                move = self.search.find_best_move(deepcopy(self.board))
                self.board.make_move(move)
                pygame.time.wait(1000)
                finding_move = False


    def play_computer(self):
        user_color = Color.WHITE
        finding_move = True
        self.board.initialise_boards()

        while self.board.game_state == GameState.NORMAL:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.board.color != user_color and not finding_move:
                    move = self.search.find_best_move(deepcopy(self.board))
                    self.board.make_move(move)
                    finding_move = True

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not self.is_piece_selected and self.board.game_state == GameState.NORMAL:
                        self.move.set_coord_from(get_coord(pos))
                        if self.board.get_format_board().get_board()[self.move.coord_from[0]][self.move.coord_from[1]] != None:
                            self.is_piece_selected = True
                    elif self.is_piece_selected:
                        self.move.set_coord_to(get_coord(pos))
                        print("Make Move")
                        self.board = self.board.make_move(self.move)
                        print("Move Made")
                        self.is_piece_selected = False
                        finding_move = False
                    else:
                        break
            if self.is_piece_selected:
                self.gui.draw_window(self.board.get_format_board(), selected_piece=self.move)
            else:
                self.gui.draw_window(self.board.get_format_board())
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
                        if self.board.get_format_board().get_board()[self.move.coord_from[0]][self.move.coord_from[1]] != None:
                            self.is_piece_selected = True
                    elif self.is_piece_selected:
                        self.move.set_coord_to(get_coord(pos))
                        print("Make Move")
                        self.board = self.board.make_move(self.move)
                        print("Move Made")
                        self.is_piece_selected = False
                    else:
                        break
            if self.is_piece_selected:
                self.gui.draw_window(self.board.get_format_board(), self.move)
            else:
                self.gui.draw_window(self.board.get_format_board())
        self.board = Board()
        self.board.initialise_boards()
        self.play_user()

if __name__ == "__main__":
    game = Game()
    game.play()
