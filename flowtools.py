from flowdata import *
import pygame
from pygame import key, freetype
from tools import FreeDrawTool, SetValueDrawTool
from toolbar import Toolbar
import math

font = freetype.SysFont("Times New Roman", 35)
def create_icon_from_text(text):
    new_icon = pygame.Surface((50,50))
    new_icon.fill((0,0,0))
    text = font.render(text, (255,255,255), style = freetype.STYLE_STRONG)
    new_icon.blit(text[0], (25-text[1].w/2, 25-text[1].h/2))
    return new_icon

def set_density(tile, value):
    if density.valid_hex_v(tile): density.hexes[tile.a][tile.b] = value
def set_positive(tile): set_density(tile, 50)
def set_negative(tile): set_density(tile, 0)

def mask(tile):
    if density.valid_hex_v(tile):
        density.mask.hexes[tile.a][tile.b] = False
        update_insulation(tile)
        for n in range(6):
            update_insulation(tile + dirs[n])
def unmask(tile):
    if density.valid_hex_v(tile, True):
        density.mask.hexes[tile.a][tile.b] = True
        update_insulation(tile)
        for n in range(6):
            update_insulation(tile + dirs[n])



draw_density_tool = FreeDrawTool(set_positive, set_negative)
draw_density_icon = pygame.Surface((50,50))
draw_density_icon.fill((0,0,255))
pygame.draw.polygon(draw_density_icon, (255,0,0), [(0,0),(30,0),(20,50),(0,50)])

draw_mask_tool = FreeDrawTool(mask, unmask)
draw_mask_icon = pygame.Surface((50,50))
draw_mask_icon.fill((0,0,0))
pygame.draw.polygon(draw_mask_icon, (255,0,255), [(0,0),(30,0),(20,50),(0,50)])


toolbar = Toolbar([draw_density_icon, draw_mask_icon], [draw_density_tool, draw_mask_tool])