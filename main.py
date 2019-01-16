from typing import List
import hexvex
from hexvex import Vex, dirs
from hexfield import *
from graphics_backend import *

import pygame
from pygame import Vector2


potential = ScalarHexField(grid_a, grid_b)
monopoles = {}

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.draw.rect(screen, (100, 100, 100), sidebar_rect)

done = False

def redraw(): draw_scalar_field(screen, potential, -50, 50, pygame.Color(0,0,255), pygame.Color(255,0,0)),

redraw()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3):
            pos = Vector2(pygame.mouse.get_pos())
            hex_pos = screen_to_hex_space(pos)
            tile = hex_pos.round()
            if tile in monopoles:
                del monopoles[tile]
            else:
                if event.button==1:
                    monopoles[tile] = Monopole(tile, 30, potential, redraw)
                else:
                    monopoles[tile] = Monopole(tile, -30, potential, redraw)
        if event.type == pygame.QUIT:
            done = True

    pygame.display.flip()
