import hexvex
import pygame

screen_width = 1000
screen_height = 700

hex_radius = 30
hex_height = 2 * hex_radius
hex_width = 2 * hex_radius * hexvex.sin60
cell_parameter = hex_width

padding = 0.15

grid_a = 10
grid_b = 10
half_hex = pygame.Vector2(hex_width / 2, hex_height / 2)
half_tile = hexvex.Vex(0.5, 0.5)
#The two are different! a hex (bounding box) is slightly larger than a tile,
#since hexes (' bounding boxes) cross into each other

game_rect = pygame.Rect(80, 0, screen_width - 80, screen_height)
sidebar_rect = pygame.Rect(0, 0, 80, screen_height)

grid_origin = game_rect.center - hexvex.Vex(grid_a-1, grid_b-1).Vector2() / 2 * cell_parameter
#Translated half a cell to the positive since hexagons are centred


hexagon = pygame.Surface((hex_width, hex_height))
hexagon.set_colorkey((0, 0, 0))
center = pygame.Vector2(hex_width / 2, hex_height / 2)
p = [None]*6
p[0] = pygame.Vector2(0, (hex_height - hex_radius) / 2)
p[1] = pygame.Vector2(0, (hex_height + hex_radius) / 2)
p[2] = pygame.Vector2(hex_width/2, hex_height)
p[3] = pygame.Vector2(hex_width, (hex_height+hex_radius)/2)
p[4] = pygame.Vector2(hex_width, (hex_height-hex_radius)/2)
p[5] = pygame.Vector2(hex_width/2, 0)
for point in p:
    point += (center - point)*(padding)
pygame.draw.polygon(hexagon, (255, 255, 255), p)


full_arrow = pygame.image.load("arrow.png")
unit_arrow = pygame.transform.scale(full_arrow, (int(hex_width), int(hex_width*770/1920)))
unit_arrow.set_colorkey((0,0,0))

def get_hexagon(color):
    colored_hex = hexagon.copy()
    colored_hex.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return colored_hex


def get_arrow(color, angle, size):
    new_arrow = pygame.transform.rotozoom(unit_arrow, -angle, size)
    new_arrow.fill(color, special_flags=pygame.BLEND_RGB_MULT)
    return new_arrow


def screen_to_hex_space(screen_pos):
    xy = (screen_pos - grid_origin) / cell_parameter
    return hexvex.vex_from_xy(xy.x, xy.y)


def hex_to_screen_space(hex_pos):
    return hex_pos.Vector2() * cell_parameter + grid_origin

def lerp_color (color1, color2, const):
    const2 = 1 - const
    return (color1.r * const + color2.r * const2, color1.g * const + color2.g * const2, color1.b * const + color2.b * const2)

def draw_scalar_field(screen, field, scale_start, scale_end, color_start, color_end):
    for i in range(grid_a):
        for j in range(grid_b):
            frac = (field.hexes[i][j]-scale_start) / (scale_end-scale_start)
            if frac < 0: frac=0
            elif frac > 1: frac = 1
            color = lerp_color(color_end, color_start, frac)
            screen.blit(get_hexagon(color), hex_to_screen_space(hexvex.Vex(i, j)) - half_hex)
            #Translated half a cell to the negative so the hexagons are centred

def draw_vector_field(screen, field, max_size_magnitude):
    for i in range(grid_a):
        for j in range(grid_b):
            polar = field.hexes[i][j].Vector2().as_polar() # (magnitude, argument)
            arrow = get_arrow((255,255,255), polar[1], polar[0] / max_size_magnitude)
            screen.blit(arrow, hex_to_screen_space(hexvex.Vex(i, j)) - (arrow.get_width()/2, arrow.get_height()/2))
