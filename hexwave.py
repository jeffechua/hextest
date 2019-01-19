from hexvex import Vex, dirs
from scalarfield import *
from vectorfield import *
from graphics_backend import *
from tools import FreeDrawTool

import pygame
from pygame import Vector2, freetype, key

# The two densities buffer each other during force application
displacement = ScalarHexField(grid_a, grid_b)
velocity = ScalarHexField(grid_a, grid_b)
acceleration = ScalarHexField(grid_a, grid_b)

pygame.init()
font = freetype.SysFont("Arial", 15)
clock = pygame.time.Clock()

done = False
paused = False

def set_velocity(tile, value):
    velocity.hexes[tile.a][tile.b] = value
    if key.get_pressed()[pygame.K_LSHIFT] or key.get_pressed()[pygame.K_LSHIFT]:
        for n in range(6):
            if velocity.validHexV(tile+dirs[n]):
                velocity.hexes[tile.a+dirs[n].a][tile.b+dirs[n].b] = value
def kick_positive(tile): set_velocity(tile, 500)
def kick_negative(tile): set_velocity(tile, -500)

current_tool = FreeDrawTool(kick_positive, kick_negative)

timescale = 1
simulation_frequency = 30
timestep = 1 / simulation_frequency
wave_speed = 10
csquared = wave_speed * wave_speed

def recalculate():
    displacement.evaluate_wave_equation(acceleration, csquared)
    acceleration.add_fraction_to(velocity, timestep)
    velocity.add_fraction_to(displacement, timestep)

def redraw():
    screen.fill((0, 0, 0), game_rect)
    draw_scalar_field_hexes(screen, displacement, -50, 50,
                      pygame.Color(0, 0, 255), pygame.Color(255, 0, 0))

pulses = []

recalculate()

while not done:

    pos = Vector2(pygame.mouse.get_pos())
    hex_pos = screen_to_hex_space(pos)
    tile = hex_pos.round()
    if not displacement.validHexV(tile):
        tile = None

    if tile != None: current_tool.before_math(tile)

    for event in pygame.event.get():
        if tile != None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_tool.mouse_down(tile)
            if event.type == pygame.MOUSEBUTTONUP:
                current_tool.mouse_up(tile)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                displacement.clear()
                velocity.clear()
        if event.type == pygame.QUIT:
            done = True

    if not paused:
        recalculate()
    
    if tile != None: current_tool.after_math(tile)
    
    redraw()

    if tile != None:
        font.render_to(screen, (game_rect.topleft[0]+10, game_rect.topleft[1]+10), str(displacement.hexes[tile.a][tile.b]), (255,255,255))
        current_tool.after_draw(tile)

    clock.tick(simulation_frequency * timescale)
    pygame.display.flip()
