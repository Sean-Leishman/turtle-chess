import math

import pygame
import numpy as np
from Constants import *
import svgutils
import io


def load_and_scale_svg(filename, scale):
    """
    Get image from a file and resize into a certain scale and return as Pygame Image

    :param filename: str
        filename representing svg file
    :param scale: float
        attribute to scale by
    :return:
        Pygame Image object of rescaled file
    """
    svg_string = open(filename, "rt").read()
    start = svg_string.find('<svg')
    if start > 0:
        svg_string = svg_string[:start+4] + f' transform="scale({scale})"' + svg_string[start+4:]

    start = svg_string.find('<g style="')
    if start > 0:
        svg_string = svg_string[:start + 10] + f'overflow=visible; ' + svg_string[start + 10:]

    svg = svgutils.compose.SVG(filename)
    svg.scale(scale)
    figure = svgutils.compose.Figure(float(svg.height) * 2, float(svg.width) * 2, svg)
    figure.save('svgNew.svg')
    svg_string = open('svgNew.svg', "rt").read()
    return pygame.image.load(io.BytesIO(svg_string.encode()))

def load_img(filename):
    return load_and_scale_svg(filename, SQUARE_SIZE / 45)

class GUI():
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        self.piecesImg = self.init_pieces_img()

    def init_pieces_img(self):
        return {
            Color.WHITE:{
                Piece.ROOK: load_img("Images\\Chess_rlt45.svg"),
                Piece.KNIGHT: load_img("Images\\Chess_nlt45.svg"),
                Piece.BISHOP: load_img("Images\\Chess_blt45.svg"),
                Piece.QUEEN: load_img("Images\\Chess_qlt45.svg"),
                Piece.KING: load_img("Images\\Chess_klt45.svg"),
                Piece.PAWN: load_img("Images\\Chess_plt45.svg"),
            },
            Color.BLACK: {
                Piece.ROOK: load_img("Images\\Chess_rdt45.svg"),
                Piece.KNIGHT: load_img("Images\\Chess_ndt45.svg"),
                Piece.BISHOP: load_img("Images\\Chess_bdt45.svg"),
                Piece.QUEEN: load_img("Images\\Chess_qdt45.svg"),
                Piece.KING: load_img("Images\\Chess_kdt45.svg"),
                Piece.PAWN: load_img("Images\\Chess_pdt45.svg"),
            }}

    def draw_window(self, board, legal_moves, selected_piece=None):
        height_offset = lambda x: ((3.5 - x) * 2) * SQUARE_SIZE
        for i in range(8):
            for j in range(8):
                if i == 0 and j == 4 or i == 7 and j == 4:
                    op = 0
                if i % 2 == 0 and j % 2 == 0 or i % 2 == 1 and j % 2 ==1:
                    pygame.draw.rect(self.screen,(153, 102, 51),(j*SQUARE_SIZE,i*SQUARE_SIZE + height_offset(i),SQUARE_SIZE,SQUARE_SIZE))
                else:
                    pygame.draw.rect(self.screen, (255, 204, 153), (j * SQUARE_SIZE, i*SQUARE_SIZE + height_offset(i), SQUARE_SIZE, SQUARE_SIZE))
                if board[i][j] is not None:
                    self.screen.blit(self.piecesImg[board[i][j][0]][board[i][j][1]],
                                     pygame.Rect(int(j * SQUARE_SIZE), int(i * SQUARE_SIZE + height_offset(i)), SQUARE_SIZE, SQUARE_SIZE))
                    if board[i][j][2]:
                        pygame.draw.rect(self.screen, (255, 0, 0),
                                         (j * SQUARE_SIZE,
                                          int(i * SQUARE_SIZE + height_offset(i)), SQUARE_SIZE, SQUARE_SIZE),
                                         2)


        if selected_piece is not None:
            pygame.draw.rect(self.screen, (255, 0, 0),
                             (selected_piece.coord_from[1] * SQUARE_SIZE, selected_piece.coord_from[0] * SQUARE_SIZE +
                              height_offset(selected_piece.coord_from[0]), SQUARE_SIZE, SQUARE_SIZE),
                             2)
            moves = legal_moves[selected_piece.coord_from[0]][selected_piece.coord_from[1]]
            for move in moves:
                pygame.draw.rect(self.screen, (0, 255, 0),
                                 (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE +
                                  height_offset(move[0]), SQUARE_SIZE, SQUARE_SIZE),
                                 2)
        #self.screen.blit(pygame.transform.rotate(self.screen, 180), (0, 0))
        pygame.display.update()

