from hexvex import *
from hexfields import *
from wavedata import grid_a, grid_b
import pygame
from pygame import freetype
import math

# Define width and height of screen here
screen_width = 1000
screen_height = 700

# Put together some reference rects and create the screen
game_rect = pygame.Rect(80, 0, screen_width - 80, screen_height)
sidebar_rect = pygame.Rect(0, 0, 80, screen_height)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.draw.rect(screen, (50, 50, 50), sidebar_rect)

# Calculate some useful constants
hex_radius = 7
hex_height = 2 * hex_radius
hex_width = 2 * hex_radius * sin60
cell_parameter = hex_width
half_hex = pygame.Vector2(hex_width / 2, hex_height / 2)
grid_origin = game_rect.center - Vex(grid_a-1, grid_b-1).Vector2() / 2 * cell_parameter

# Pre-load vertices for a unit hexagon that is frequently used
center = pygame.Vector2(hex_width / 2, hex_height / 2)
unit_hex = [None]*6
unit_hex[0] = pygame.Vector2(-hex_width/2, - hex_radius/2)
unit_hex[1] = pygame.Vector2(-hex_width/2, hex_radius/2)
unit_hex[2] = pygame.Vector2(0, hex_height/2)
unit_hex[3] = pygame.Vector2(hex_width/2, hex_radius/2)
unit_hex[4] = pygame.Vector2(hex_width/2, -hex_radius/2)
unit_hex[5] = pygame.Vector2(0, -hex_height/2)

# Utility class - maps a numerical scale to corresponding interpolations between two colors
class Spectrum:
    def __init__(self, scale_start, scale_end, color_start, color_end):
        self.scale_start = scale_start
        self.scale_end = scale_end
        self.colors = []
        self.surfaces = []
        for i in range(scale_start, scale_end + 1):
            self.colors.append(lerp_color(color_end, color_start, (i-scale_start)/(scale_end-scale_start)))
    def retrieve(self, index):
        return self.colors[round(clamp(index, self.scale_start, self.scale_end)) - self.scale_start]

# Utility functions to lock and unlock toolbar pane for drawing
def restrict_drawing():
    screen.set_clip(game_rect)
def free_drawing():
    screen.set_clip(None)

# Utilities for drawing text onscreen
freetype.init()
font = freetype.SysFont("Arial", 15)
def print_topleft(text, x_offset, y_offset):
    font.render_to(screen, (game_rect.topleft[0]+x_offset, game_rect.topleft[1]+y_offset), text, (255,255,255))
def print_bottomleft(text, x_offset, y_offset):
    font.render_to(screen, (game_rect.bottomleft[0]+x_offset, game_rect.bottomleft[1]+y_offset-15), text, (255,255,255))
def print_bottomright(text, x_offset, y_offset):
    surf = font.render(text, (255,255,255))[0]
    screen.blit(surf, (game_rect.bottomright[0] - surf.get_width() + x_offset,
                      game_rect.bottomright[1] - 15 + y_offset))
def print_topright(text, x_offset, y_offset):
    surf = font.render(text, (255,255,255))[0]
    screen.blit(surf, (game_rect.topright[0] - surf.get_width() + x_offset,
                      game_rect.topright[1] + y_offset))

# Utility functions to convert from screen space to hexagonal space
def screen_to_hex_space(screen_pos):
    pos = (screen_pos - grid_origin) / cell_parameter
    a = pos.y / sin60
    b = pos.x + a / 2
    return Vex(a,b)
def hex_to_screen_space(hex_pos):
    return hex_pos.Vector2() * cell_parameter + grid_origin

# Utility function for linear interpolation of color
def lerp_color(color1, color2, const):
    const2 = 1 - const
    return pygame.Color(round(color1.r * const + color2.r * const2),
            round(color1.g * const + color2.g * const2),
            round(color1.b * const + color2.b * const2))

# Self-explanatory utility function
# This shouldn't really be here, but it's often-used and this module is commonly imported
def clamp(value, minvalue, maxvalue):
    return max(minvalue, min(value, maxvalue))

# Draws a hexagon onscreen using a particular blend mode
temp_surf = pygame.Surface((int(hex_width), int(hex_height)))
temp_surf.set_colorkey((0,0,0))
offset_unit_hex = list(map(lambda v : v + half_hex, unit_hex))
def blend_hexagon(pos, color, flags):
    temp_surf.fill((0,0,0))
    pygame.draw.polygon(temp_surf, color, offset_unit_hex)
    screen.blit(temp_surf, pos-half_hex, special_flags = flags)

# Draws a hexagon onscreen without blending - faster
def draw_hexagon(pos, color):
    translated_hex = list(map(lambda v : v + pos, unit_hex))
    pygame.draw.polygon(screen, color, translated_hex)

# Draws hexagons to represent a scalar field, mapping the value of each cell to a color in the spectrum
def draw_scalar_field(screen, field, spectrum):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                draw_hexagon(hex_to_screen_space(Vex(i, j)), spectrum.retrieve(field.hexes[i][j]))