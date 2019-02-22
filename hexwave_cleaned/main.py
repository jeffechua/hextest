import pyximport
pyximport.install()

from hexvex import *
from hexfields import *
from graphics import *
from wavedata import *
from wavetools import toolbar
import tools

import pygame
from pygame import Vector2, key

# Initial set-up stuff

pygame.init()

done = False
paused = False
clock = pygame.time.Clock()

# Variables for tracking performance

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

# Variables and set-up for visual effects

spectrum = Spectrum(-50, 50, pygame.Color(0, 0, 255), pygame.Color(255, 0, 0))
blur = False

# Main loop

while not done:

    pos = Vector2(pygame.mouse.get_pos())
    hex_pos = screen_to_hex_space(pos)
    tile = hex_pos.round()

    toolbar.tools[toolbar.current].before_math(tile)

    for event in pygame.event.get():

        # Pipes mouse input into the currently selected tool
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

        # Handles key input
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_c: # C: clear all state (psi, psi', psi'') information
                displacement.clear()
                velocity.clear()
            if event.key == pygame.K_r: # R: clear everything, including masking, speed and damping
                displacement.clear()
                velocity.clear()
                wave_speed.reset()
                csquared.reset()
                damping.reset()
                damp_multiplier.reset()
                displacement.mask.clear()
            if event.key == pygame.K_b: # B: toggle blurring of the main simulation display
                blur = not blur
            if event.key == pygame.K_EQUALS: # Increase brush size
                toolbar.tools[toolbar.current].mouse_scroll(+1)
            if event.key == pygame.K_MINUS:  # Decrease brush size
                toolbar.tools[toolbar.current].mouse_scroll(-1)
        if event.type == pygame.QUIT:
            done = True

    # A bunch of stuff that essentially tries to fix simulation framerate at the
    # preset in wavedata, and filling the rest of available time with draw frames.
    # Also computes some simulation performance information.
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
    
    # Trigger anything the current tool wants to do after math
    toolbar.tools[toolbar.current].after_math(tile)
    
    # Mark when we start drawing
    t = pygame.time.get_ticks()

    # Draw simulation
    screen.fill((0, 0, 0), game_rect)
    draw_scalar_field(screen, displacement, spectrum)
    if blur:
        screen.blit(pygame.transform.smoothscale(pygame.transform.smoothscale(screen,
        (int(screen_width/10),int(screen_height/10))), (int(screen_width), int(screen_height))), (0,0))
    # Display info text
    if displacement.valid_hex_v(tile):
        print_topleft("ψ: " + str(displacement.hexes[tile.a][tile.b]), 10, 10)
        print_topleft("ψ': " + str(velocity.hexes[tile.a][tile.b]), 10, 30)
        print_topleft("ψ'': " + str(laplace.hexes[tile.a][tile.b] * csquared.hexes[tile.a][tile.b]), 10, 50)
    print_bottomleft("simulation framerate: " + str(sim_framerate), 10, -10)
    print_bottomleft("draw framerate: " + str(draw_framerate), 10, -30)
    print_bottomleft("stutter frequency: " + str(stutter_frequency), 10, -50)
    print_bottomright("average simulation step (ms): " + str(avg_sim_time_cost), -10, -10)
    print_bottomright("average draw step (ms): " + str(avg_draw_time_cost), -10, -30)
    
    # Trigger anything the current tool wants to do after drawing
    toolbar.tools[toolbar.current].after_draw(tile)
    
    # Compute drawing performance information
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
    
    # Display changes
    pygame.display.flip()
