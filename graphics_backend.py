import hexvex
import pygame
import math
from pygame import freetype

screen_width = 1000
screen_height = 700

hex_radius = 7
hex_height = 2 * hex_radius
hex_width = 2 * hex_radius * hexvex.sin60
cell_parameter = hex_width

padding = 0.15
hex_draw_radius = hex_radius - padding

half_hex = pygame.Vector2(hex_width / 2, hex_height / 2)
half_tile = hexvex.Vex(0.5, 0.5)
# The two are different! a hex (bounding box) is slightly larger than a tile,
# since hexes (' bounding boxes) cross into each other

game_rect = pygame.Rect(80, 0, screen_width - 80, screen_height)
sidebar_rect = pygame.Rect(0, 0, 80, screen_height)

def gen_origin(a, b):
    global grid_origin
    grid_origin = game_rect.center - \
        hexvex.Vex(a-1, b-1).Vector2() / 2 * cell_parameter
# Translated half a cell to the positive since hexagons are centred

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.draw.rect(screen, (50, 50, 50), sidebar_rect)

freetype.init()
font = freetype.SysFont("Arial", 15)

center = pygame.Vector2(hex_width / 2, hex_height / 2)
p = [None]*6
p[0] = pygame.Vector2(-hex_width/2, - hex_radius/2)
p[1] = pygame.Vector2(-hex_width/2, hex_radius/2)
p[2] = pygame.Vector2(0, hex_height/2)
p[3] = pygame.Vector2(hex_width/2, hex_radius/2)
p[4] = pygame.Vector2(hex_width/2, -hex_radius/2)
p[5] = pygame.Vector2(0, -hex_height/2)
p2 = p.copy()
for i in range(len(p)): p[i] = p[i] * (1 - padding)


full_arrow = pygame.image.load("arrow.png")
unit_arrow = pygame.transform.scale(
    full_arrow, (int(hex_width), int(hex_width*770/1920)))
unit_arrow.set_colorkey((0, 0, 0))


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

def restrict_drawing():
    screen.set_clip(game_rect)

def free_drawing():
    screen.set_clip(None)

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

temp_surf = pygame.Surface((int(hex_width), int(hex_height)))
temp_surf.set_colorkey((0,0,0))
offset_p2 = list()
for i in range(6): offset_p2.append(p2[i] + half_hex)
def draw_combine_back_hexagon(pos, color, flags):
    temp_surf.fill((0,0,0))
    pygame.draw.polygon(temp_surf, color, offset_p2)
    screen.blit(temp_surf, pos-half_hex, special_flags = flags)

def draw_hexagon(pos, color):
    new_points = p.copy()
    for i in range(len(new_points)): new_points[i] = new_points[i] + pos
    pygame.draw.polygon(screen, color, new_points)

def draw_back_hexagon(pos, color):
    new_points = p2.copy()
    for i in range(len(new_points)): new_points[i] = new_points[i] + pos
    pygame.draw.polygon(screen, color, new_points)

def get_arrow(color, angle, size):
    new_arrow = pygame.transform.rotozoom(unit_arrow, -angle, size)
    new_arrow.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return new_arrow


def screen_to_hex_space(screen_pos):
    xy = (screen_pos - grid_origin) / cell_parameter
    return hexvex.vex_from_xy(xy.x, xy.y)


def hex_to_screen_space(hex_pos):
    return hex_pos.Vector2() * cell_parameter + grid_origin


def lerp_color(color1, color2, const):
    const2 = 1 - const
    return pygame.Color(round(color1.r * const + color2.r * const2),
            round(color1.g * const + color2.g * const2),
            round(color1.b * const + color2.b * const2))


def clamp(value, minvalue, maxvalue):
    return max(minvalue, min(value, maxvalue))


def draw_scalar_field_hexes(screen, field, spectrum):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                draw_hexagon(hex_to_screen_space(hexvex.Vex(i, j)), spectrum.retrieve(field.hexes[i][j]))
                # Translated half a cell to the negative so the hexagons are centred

def draw_scalar_field_back_hexes(screen, field, spectrum):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                draw_back_hexagon(hex_to_screen_space(hexvex.Vex(i, j)), spectrum.retrieve(field.hexes[i][j]))
                # Translated half a cell to the negative so the hexagons are centred

def draw_mask_hexes(screen, mask, color):
    for i in range(mask.a):
        for j in range(mask.b):
            if mask.hexes[i][j]:
                draw_hexagon(hex_to_screen_space(hexvex.Vex(i, j)), color)

def draw_mask_back_hexes(screen, mask, color):
    for i in range(mask.a):
        for j in range(mask.b):
            if mask.hexes[i][j]:
                draw_back_hexagon(hex_to_screen_space(hexvex.Vex(i, j)), color)

def draw_scalar_field_rects(screen, field, spectrum):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                pos = hex_to_screen_space(hexvex.Vex(i, j))
                pygame.draw.rect(screen, spectrum.retrieve(field.hexes[i][j]), pygame.Rect(int(pos.x-hex_draw_radius), int(pos.y-hex_draw_radius), int(hex_draw_radius*2), int(hex_draw_radius*2)))

def draw_scalar_field_circles_color(screen, field, spectrum):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                pos = hex_to_screen_space(hexvex.Vex(i, j))
                pygame.draw.circle(screen, spectrum.retrieve(field.hexes[i][j]), (int(pos.x), int(pos.y)), int(hex_draw_radius))

def draw_scalar_field_circles_radii(screen, field, scale_start, scale_end, max_radius, color=(0, 0, 0)):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                radius = max_radius * \
                    (field.hexes[i][j]-scale_start) / (scale_end-scale_start)
                radius = clamp(radius, 0, max_radius)
                pos = hex_to_screen_space(hexvex.Vex(i, j))
                pygame.draw.circle(screen, color, (int(pos.x), int(pos.y)), int(radius))


def draw_vector_field(screen, field, max_size_magnitude):
    for i in range(field.a):
        for j in range(field.b):
            if field.valid_hex(i,j):
                # (magnitude, argument)
                polar = field.hexes[i][j].Vector2().as_polar()
                arrow = get_arrow(
                    (255, 255, 255), polar[1], polar[0] / max_size_magnitude)
                screen.blit(arrow, hex_to_screen_space(hexvex.Vex(i, j)) - (arrow.get_width()/2, arrow.get_height()/2))