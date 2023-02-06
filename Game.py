
from Constants import *
from GUI import GUI
import pygame, sys
from Move import Move

def get_move():
    src = input("From: ")
    dest = input("To: ")
    return Move(Square.from_str(src), Square.from_str(dest), promo_piece)

class Game():
    def __init__(self):
        pygame.init()
        self.board = Board()
        #self.gui = GUI()

    def play(self):
        self.board.init_game()
        while True:
            print("Enter your move")
            print("\n")
            player_move = get_move()
            board = board.apply_move(player_move)
            print("\n")
            print("Board is now:")
            print(board)
            print("\n")

if __name__ == "__main__":
    Game().play()
