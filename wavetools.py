from wavedata import *
import pygame
from pygame import key
from tools import FreeDrawTool
from toolbar import Toolbar

def set_velocity(tile, value):
    if velocity.valid_hex_v(tile): velocity.hexes[tile.a][tile.b] = value
def kick_positive(tile): set_velocity(tile, 500)
def kick_negative(tile): set_velocity(tile, -500)

def mask(tile):
    if displacement.valid_hex_v(tile): displacement.mask.hexes[tile.a][tile.b] = False
def unmask(tile):
    if displacement.valid_hex_v(tile, True): displacement.mask.hexes[tile.a][tile.b] = True

draw_velocity_tool = FreeDrawTool(kick_positive, kick_negative)
draw_velocity_icon = pygame.Surface((50,50))
draw_velocity_icon.fill((0,0,255))
pygame.draw.polygon(draw_velocity_icon, (255,0,0), [(0,0),(30,0),(20,50),(0,50)])

draw_mask_tool = FreeDrawTool(mask, unmask)
draw_mask_icon = pygame.Surface((50,50))
draw_mask_icon.fill((0,0,0))
pygame.draw.polygon(draw_mask_icon, (255,0,255), [(0,0),(30,0),(20,50),(0,50)])

toolbar = Toolbar([draw_velocity_icon, draw_mask_icon], [draw_velocity_tool, draw_mask_tool])