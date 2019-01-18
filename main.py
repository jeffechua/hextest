from typing import List
import hexvex
from hexvex import Vex, dirs
from hexfield import *
from graphics_backend import *

import pygame
from pygame import Vector2

# The two densities buffer each other during force application
density = ScalarHexField(grid_a, grid_b, default_value = 5)
density_buffer = ScalarHexField(grid_a, grid_b, default_value = 5)
current = False
monopoles = {}
dynamic_potential = ScalarHexField(grid_a, grid_b)
static_potential = ScalarHexField(grid_a, grid_b)
potential = ScalarHexField(grid_a, grid_b)
force = VectorHexField(grid_a, grid_b)

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.draw.rect(screen, (100, 100, 100), sidebar_rect)

done = False
paused = False

show_forces = True
show_potential = True
show_density = True

def recalculate():
    global potential, force
    potential.clone(static_potential, multiplier=-1)
    potential += dynamic_potential
    potential.grad(force)
    force *= -1
    redraw()


def redraw():
    screen.fill((0, 0, 0), game_rect)
    draw_scalar_field_back_hexes(screen, potential, -50, 50,
                      pygame.Color(0, 0, 255), pygame.Color(255, 0, 0))
    draw_scalar_field_hexes(screen, density, 0, 50,
                      pygame.Color(10, 10, 10), pygame.Color(30, 100, 0))
    draw_vector_field(screen, force, 30)


recalculate()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 1 or event.button == 3):
            pos = Vector2(pygame.mouse.get_pos())
            hex_pos = screen_to_hex_space(pos)
            tile = hex_pos.round()
            if tile in monopoles:
                del monopoles[tile]
            else:
                if event.button==1:
                    monopoles[tile] = Monopole(tile, 30, static_potential, recalculate)
                else:
                    monopoles[tile] = Monopole(tile, -30, static_potential, recalculate)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
        if event.type == pygame.QUIT:
            done = True
    if not paused:
        force.apply_to(density, density_buffer, 0.02)
        density_buffer.dissolve_maxima(density, force, 1, 0.02)
        dynamic_potential = density
        recalculate()
    clock.tick(30)
    pygame.display.flip()
