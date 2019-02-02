from wavedata import *
import pygame
from pygame import key
from tools import FreeDrawTool, SetValueDrawTool
from toolbar import Toolbar

def set_displacement(tile, value):
    if displacement.valid_hex_v(tile): displacement.hexes[tile.a][tile.b] = value
def set_positive(tile): set_displacement(tile, 30)
def set_negative(tile): set_displacement(tile, -30)

def mask(tile):
    if displacement.valid_hex_v(tile): displacement.mask.hexes[tile.a][tile.b] = False
def unmask(tile):
    if displacement.valid_hex_v(tile, True): displacement.mask.hexes[tile.a][tile.b] = True

def set_wave_speed(tile, value):
    if not wave_speed.valid_hex_v(tile): return
    wave_speed.hexes[tile.a][tile.b] = value
    csquared.hexes[tile.a][tile.b] = value * value

draw_velocity_tool = FreeDrawTool(set_positive, set_negative)
draw_velocity_icon = pygame.Surface((50,50))
draw_velocity_icon.fill((0,0,255))
pygame.draw.polygon(draw_velocity_icon, (255,0,0), [(0,0),(30,0),(20,50),(0,50)])

draw_mask_tool = FreeDrawTool(mask, unmask)
draw_mask_icon = pygame.Surface((50,50))
draw_mask_icon.fill((0,0,0))
pygame.draw.polygon(draw_mask_icon, (255,0,255), [(0,0),(30,0),(20,50),(0,50)])

set_speed_tool = SetValueDrawTool(wave_speed, 9, 1, 9, 1, left_draw = set_wave_speed) #set_wave_speed defined in 
set_speed_icon = pygame.Surface((50,50))
set_speed_icon.fill((0,0,0))
pygame.draw.circle(set_speed_icon, (255,255,255), (25,25), 15, 7)
pygame.draw.rect(set_speed_icon, (0,0,0), pygame.Rect(25, 20, 20, 10))

toolbar = Toolbar([draw_velocity_icon, draw_mask_icon, set_speed_icon], [draw_velocity_tool, draw_mask_tool, set_speed_tool])