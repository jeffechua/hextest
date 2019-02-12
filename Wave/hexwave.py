import sys
sys.path.append(sys.path[0][:-len("/Flow")])

import pyximport
pyximport.install()

from hexvex import Vex, dirs
from scalarfield import *
from graphics_backend import *
from wavedata import *
from wavetools import toolbar
import tools

import pygame
from pygame import Vector2, key


pygame.init()

done = False
paused = False
clock = pygame.time.Clock()

net_simulated_time = 0

sim_step_counter = 0
time_for_ten_sim_steps = 0
sim_framerate = 0
ten_sims_time_cost = 0
avg_sim_time_cost = 0

draw_counter = 0
time_for_ten_draws = 0
draw_framerate = 0
ten_draws_time_cost = 0
avg_draw_time_cost = 0

stutter_counter = 0
stutter_frequency = 0,

spectrum = Spectrum(-50, 50, pygame.Color(0, 0, 255), pygame.Color(255, 0, 0))
blur = False

gen_origin(grid_a, grid_b)

def redraw():
    screen.fill((0, 0, 0), game_rect)
    draw_scalar_field_back_hexes(screen, displacement, spectrum)
    if blur:
        screen.blit(pygame.transform.smoothscale(pygame.transform.smoothscale(screen, (int(screen_width/10),int(screen_height/10))), (int(screen_width), int(screen_height))), (0,0))

while not done:

    pos = Vector2(pygame.mouse.get_pos())
    hex_pos = screen_to_hex_space(pos)
    tile = hex_pos.round()

    toolbar.tools[toolbar.current].before_math(tile)

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                if tools.controlling() or tools.shifting():
                    toolbar.tools[toolbar.current].mouse_scroll(+1)
                else:
                    toolbar.increment_selection()
            elif event.button == 5:
                if tools.controlling() or tools.shifting():
                    toolbar.tools[toolbar.current].mouse_scroll(-1)
                else:
                    toolbar.decrement_selection()
            else:
                toolbar.tools[toolbar.current].mouse_down(tile)
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
                wave_speed.reset()
                csquared.reset()
                damping.reset()
                damp_multiplier.reset()
                displacement.mask.clear()
            if event.key == pygame.K_b:
                blur = not blur
            if event.key == pygame.K_EQUALS:
                toolbar.tools[toolbar.current].mouse_scroll(+1)
            if event.key == pygame.K_MINUS:
                toolbar.tools[toolbar.current].mouse_scroll(-1)
        if event.type == pygame.QUIT:
            done = True

    if paused:
        net_simulated_time = pygame.time.get_ticks()
    else:
        if net_simulated_time > pygame.time.get_ticks():
            pygame.time.wait(math.ceil(pygame.time.get_ticks() - net_simulated_time))
            stutter_counter += 1
        while net_simulated_time < pygame.time.get_ticks():
            if pygame.time.get_ticks() - net_simulated_time > 1000:
                net_simulated_time = pygame.time.get_ticks() + 100
            t = pygame.time.get_ticks()
            simulate_step()
            ten_sims_time_cost += pygame.time.get_ticks() - t
            net_simulated_time += timestep * 1000.0 # timestep is in s, ticks is in ms
            sim_step_counter += 1
            if sim_step_counter == 10:
                sim_step_counter = 0
                sim_framerate = 10000 / (pygame.time.get_ticks() - time_for_ten_sim_steps)
                avg_sim_time_cost = ten_sims_time_cost / 10
                ten_sims_time_cost = 0
                time_for_ten_sim_steps = pygame.time.get_ticks()
    
    
    toolbar.tools[toolbar.current].after_math(tile)
    
    t = pygame.time.get_ticks()

    redraw()
    if displacement.valid_hex_v(tile):
        print_topleft("ψ: " + str(displacement.hexes[tile.a][tile.b]), 10, 10)
        print_topleft("ψ': " + str(velocity.hexes[tile.a][tile.b]), 10, 30)
        print_topleft("ψ'': " + str(laplace.hexes[tile.a][tile.b] * csquared.hexes[tile.a][tile.b]), 10, 50)

    print_bottomleft("simulation framerate: " + str(sim_framerate), 10, -10)
    print_bottomleft("draw framerate: " + str(draw_framerate), 10, -30)
    print_bottomleft("stutter frequency: " + str(stutter_frequency), 10, -50)
    print_bottomright("average simulation step (ms): " + str(avg_sim_time_cost), -10, -10)
    print_bottomright("average draw step (ms): " + str(avg_draw_time_cost), -10, -30)
    
    toolbar.tools[toolbar.current].after_draw(tile)
    
    ten_draws_time_cost += pygame.time.get_ticks() - t

    draw_counter += 1
    if draw_counter == 10:
        draw_framerate = 10000 / (pygame.time.get_ticks() - time_for_ten_draws)
        avg_draw_time_cost = ten_draws_time_cost / 10
        stutter_frequency = 1000 * stutter_counter / (pygame.time.get_ticks() - time_for_ten_draws)
        draw_counter = 0
        stutter_counter = 0
        ten_draws_time_cost = 0
        time_for_ten_draws = pygame.time.get_ticks()
    
    pygame.display.flip()
