from hexvex import Vex, dirs
from scalarfield import *
from vectorfield import *
from graphics_backend import *

import pygame
from pygame import Vector2, freetype

# The two densities buffer each other during force application
displacement = ScalarHexField(grid_a, grid_b)
velocity = ScalarHexField(grid_a, grid_b)
acceleration = ScalarHexField(grid_a, grid_b)

pygame.init()
font = freetype.SysFont("Arial", 15)
clock = pygame.time.Clock()

done = False
paused = False

timescale = 1
simulation_frequency = 30
timestep = 1 / simulation_frequency
wave_speed = 3
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

    for event in pygame.event.get():
        if tile != None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    velocity.hexes[tile.a][tile.b] = 1000
                if event.button == 3:
                    velocity.hexes[tile.a][tile.b] = 1000
                    for n in range(6):
                        if velocity.validHexV(tile+dirs[n]):
                            velocity.hexes[tile.a+dirs[n].a][tile.b+dirs[n].b] = 1000
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
        if event.type == pygame.QUIT:
            done = True

    if not paused:
        recalculate()
    
    
    redraw()
    if tile != None:
        font.render_to(screen, (game_rect.topleft[0]+10, game_rect.topleft[1]+10), str(displacement.hexes[tile.a][tile.b]), (255,255,255))

    clock.tick(simulation_frequency * timescale)
    pygame.display.flip()
