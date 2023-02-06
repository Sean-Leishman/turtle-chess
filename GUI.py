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
    print(svg_string)
    return pygame.image.load(io.BytesIO(svg_string.encode()))

def load_img(filename):
    return load_and_scale_svg(filename, SQUARE_SIZE / 45)

class GUI():
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        self.piecesImg = self.init_pieces_img()

    def init_pieces_img(self):
        return {
            'R': load_img("Images\\Chess_rlt45.svg"),
            'N': load_img("Images\\Chess_nlt45.svg"),
            'B': load_img("Images\\Chess_blt45.svg"),
            'Q': load_img("Images\\Chess_qlt45.svg"),
            'K': load_img("Images\\Chess_klt45.svg"),
            'P': load_img("Images\\Chess_plt45.svg"),
            'r': load_img("Images\\Chess_rdt45.svg"),
            'n': load_img("Images\\Chess_ndt45.svg"),
            'b': load_img("Images\\Chess_bdt45.svg"),
            'q': load_img("Images\\Chess_qdt45.svg"),
            'k': load_img("Images\\Chess_kdt45.svg"),
            'p': load_img("Images\\Chess_pdt45.svg"),
        }

    def draw_window(self, board):
        for i in range(8):
            for j in range(8):
                if i % 2 == 0 and j % 2 == 0 or i % 2 == 1 and j % 2 ==1:
                    pygame.draw.rect(self.screen,(153, 102, 51),(i*SQUARE_SIZE,j*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE))
                else:
                    pygame.draw.rect(self.screen, (255, 204, 153), (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                if board[i][j] != "":
                    self.screen.blit(self.piecesImg[board[i][j]],
                                     pygame.Rect(i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pygame.display.update()

