import hexvex
from hexvex import Vex, dirs
from hexfield import *
import pygame
from pygame import Vector2

hex_radius = 25
hex_height = 2 * hex_radius
hex_width = 2 * hex_radius * hexvex.sin60
cell_parameter = hex_width

padding = 0.15

grid_a = 7
grid_b = 7
half_hex = Vector2(hex_width/2, hex_height/2)
half_tile = Vex(0.5, 0.5)
"""The two are different! a hex (bounding box) is slightly larger than a tile,
since hexes (' bounding boxes) cross into each other"""
screen_origin = Vex(0, grid_a / 2).Vector2() * cell_parameter + half_hex
"""Translated half a cell to the positive since hexagons are centred"""

def screen_to_hex_space(screen_pos):
    xy = (screen_pos - screen_origin) / cell_parameter
    return hexvex.vex_from_xy(xy.x, xy.y)

def hex_to_screen_space(hex_pos):
    return hex_pos.Vector2() * cell_parameter + screen_origin


pygame.init()
screen = pygame.display.set_mode((800, 600))
done = False
clock = pygame.time.Clock()

hexagon = pygame.Surface((hex_width, hex_height))
hexagon.set_colorkey((0,0,0))
hexagon.set_alpha(50)
center = pygame.math.Vector2(hex_width / 2, hex_height / 2)
p = [None]*6
p[0] = Vector2(0, (hex_height - hex_radius) / 2)
p[1] = Vector2(0, (hex_height + hex_radius) / 2)
p[2] = Vector2(hex_width/2, hex_height)
p[3] = Vector2(hex_width, (hex_height+hex_radius)/2)
p[4] = Vector2(hex_width, (hex_height-hex_radius)/2)
p[5] = Vector2(hex_width/2, 0)
for point in p:
    point += (center - point)*(padding)
pygame.draw.polygon(hexagon, (255, 255, 255), p)


for i in range(grid_a):
    for j in range(grid_b):
        screen.blit(hexagon, hex_to_screen_space(Vex(i,j)) - half_hex)
        """Translated half a cell to the negative so the hexagons are centred"""

while not done:
    for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = Vector2(pygame.mouse.get_pos())
                hex_pos = screen_to_hex_space(pos)
                tile = hex_pos.round()
                screen.blit(hexagon, hex_to_screen_space(tile) - half_hex)
            if event.type == pygame.QUIT:
                done = True
    
    pygame.display.flip()