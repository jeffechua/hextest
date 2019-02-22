from wavedata import *
import pygame
from pygame import key, freetype
from tools import FreeDrawTool, SetValueDrawTool, Toolbar
import math

font = freetype.SysFont("Times New Roman", 35)
def create_icon_from_text(text):
    new_icon = pygame.Surface((50,50))
    new_icon.fill((0,0,0))
    text = font.render(text, (255,255,255), style = freetype.STYLE_STRONG)
    new_icon.blit(text[0], (25-text[1].w/2, 25-text[1].h/2))
    return new_icon

def set_positive(tile):
    if displacement.valid_hex_v(tile): displacement.hexes[tile.a][tile.b] =  30
def set_negative(tile):
    if displacement.valid_hex_v(tile): displacement.hexes[tile.a][tile.b] = -30

def mask(tile):
    if displacement.valid_hex_v(tile):       displacement.mask.hexes[tile.a][tile.b] = False
def unmask(tile):
    if displacement.valid_hex_v(tile, True): displacement.mask.hexes[tile.a][tile.b] = True

def set_wave_speed(tile, value):
    if not wave_speed.valid_hex_v(tile): return
    wave_speed.hexes[tile.a][tile.b] = value
    csquared.hexes[tile.a][tile.b] = value * value
def unset_wave_speed(tile, value): # set to "default" of 9
    if not wave_speed.valid_hex_v(tile): return
    wave_speed.hexes[tile.a][tile.b] = 9
    csquared.hexes[tile.a][tile.b] = 81

def set_damping(tile, value):
    if not damping.valid_hex_v(tile): return
    damping.hexes[tile.a][tile.b] = value
    damp_multiplier.hexes[tile.a][tile.b] = math.exp(-value*timestep)
def unset_damping(tile, value): # set to "default" of 0
    if not damping.valid_hex_v(tile): return
    damping.hexes[tile.a][tile.b] = 0
    damp_multiplier.hexes[tile.a][tile.b] = 1

# Basic tool for perturbing the surface
draw_displacement_tool = FreeDrawTool(set_positive, set_negative)
draw_displacement_icon = pygame.Surface((50,50))
draw_displacement_icon.fill((0,0,255))
pygame.draw.polygon(draw_displacement_icon, (255,0,0), [(0,0),(30,0),(20,50),(0,50)])

# Masks which areas to exclude from the simulation, making "walls"
draw_mask_tool = FreeDrawTool(mask, unmask)
draw_mask_icon = pygame.Surface((50,50))
draw_mask_icon.fill((0,0,0))
pygame.draw.polygon(draw_mask_icon, (255,0,255), [(0,0),(30,0),(20,50),(0,50)])

# Sets local wave propagation speed
set_speed_tool = SetValueDrawTool(wave_speed, 9, 1, 9, 1, left_draw = set_wave_speed, right_draw = unset_wave_speed)
set_speed_icon = create_icon_from_text("c")

# Sets local damping factor
set_damping_tool = SetValueDrawTool(damping, 3, 0, 9, 1, left_draw = set_damping, right_draw = unset_damping)
set_damping_icon = create_icon_from_text("γ")

# Sets up toolbar
toolbar = Toolbar([draw_displacement_icon, draw_mask_icon, set_speed_icon, set_damping_icon], [draw_displacement_tool, draw_mask_tool, set_speed_tool, set_damping_tool])
