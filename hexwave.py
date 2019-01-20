from hexvex import Vex, dirs
from scalarfield import *
from vectorfield import *
from graphics_backend import *
from wavedata import *
from wavetools import toolbar
from tools import FreeDrawTool

import pygame
from pygame import Vector2, freetype, key


pygame.init()
font = freetype.SysFont("Arial", 15)
clock = pygame.time.Clock()

done = False
paused = False

def redraw():
    screen.fill((0, 0, 0), game_rect)
    draw_scalar_field_hexes(screen, displacement, -50, 50,
                      pygame.Color(0, 0, 255), pygame.Color(255, 0, 0))

while not done:

    pos = Vector2(pygame.mouse.get_pos())
    hex_pos = screen_to_hex_space(pos)
    tile = hex_pos.round()

    toolbar.tools[toolbar.current].before_math(tile)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            toolbar.tools[toolbar.current].mouse_down(tile)
            if event.button == 4:
                toolbar.increment_selection()
            elif event.button == 5:
                toolbar.decrement_selection()
        if event.type == pygame.MOUSEBUTTONUP:
            toolbar.tools[toolbar.current].mouse_up(tile)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_c:
                displacement.clear()
                velocity.clear()
            if event.key == pygame.K_r:
                displacement.clear()
                velocity.clear()
                displacement.mask.clear()
        if event.type == pygame.QUIT:
            done = True

    if not paused:
        recalculate()
    
    toolbar.tools[toolbar.current].after_math(tile)
    
    redraw()

    if displacement.valid_hex_v(tile):
        font.render_to(screen, (game_rect.topleft[0]+10, game_rect.topleft[1]+10), str(displacement.hexes[tile.a][tile.b]), (255,255,255))

    toolbar.tools[toolbar.current].after_draw(tile)

    clock.tick(simulation_frequency * timescale)
    pygame.display.flip()
