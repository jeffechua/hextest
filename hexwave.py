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

done = False
paused = False
clock = pygame.time.Clock()

net_simulated_time = 0
sim_frame_counter = 0
sim_frame_counting_time = 0
sim_framerate = 0
draw_frame_counter = 0
draw_frame_counting_time = 0
draw_framerate = 0
stutter_counter = 0
stutter_frequency = 0

spectrum = Spectrum(-50, 50, pygame.Color(0, 0, 255), pygame.Color(255, 0, 0))

def redraw():
    screen.fill((0, 0, 0), game_rect)
    draw_scalar_field_back_hexes(screen, displacement, spectrum)

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

    if paused:
        net_simulated_time = pygame.time.get_ticks()
    else:
        if net_simulated_time > pygame.time.get_ticks():
            pygame.time.wait(math.ceil(pygame.time.get_ticks() - net_simulated_time))
            stutter_counter += 1
        while net_simulated_time < pygame.time.get_ticks():
            if pygame.time.get_ticks() - net_simulated_time > 1000:
                net_simulated_time = pygame.time.get_ticks() + 100
            simulate_step()
            net_simulated_time += timestep * 1000.0 # timestep is in s, ticks is in ms
            sim_frame_counter += 1
            if sim_frame_counter == 10:
                sim_frame_counter = 0
                sim_framerate = 10000 / (pygame.time.get_ticks() - sim_frame_counting_time)
                sim_frame_counting_time = pygame.time.get_ticks()
    
    
    toolbar.tools[toolbar.current].after_math(tile)
    
    redraw()
    if displacement.valid_hex_v(tile):
        font.render_to(screen, (game_rect.topleft[0]+10, game_rect.topleft[1]+10), "x: " + str(displacement.hexes[tile.a][tile.b]), (255,255,255))
        font.render_to(screen, (game_rect.topleft[0]+10, game_rect.topleft[1]+30), "x': " + str(velocity.hexes[tile.a][tile.b]), (255,255,255))
        font.render_to(screen, (game_rect.topleft[0]+10, game_rect.topleft[1]+50), "x'': " + str(acceleration.hexes[tile.a][tile.b]), (255,255,255))
    font.render_to(screen, (game_rect.bottomleft[0]+10, game_rect.bottomleft[1]-25), "simulation framerate: " + str(sim_framerate), (255,255,255))
    font.render_to(screen, (game_rect.bottomleft[0]+10, game_rect.bottomleft[1]-45), "draw framerate: " + str(draw_framerate), (255,255,255))
    font.render_to(screen, (game_rect.bottomleft[0]+10, game_rect.bottomleft[1]-65), "stutter frequency: " + str(stutter_frequency), (255,255,255))
    toolbar.tools[toolbar.current].after_draw(tile)
    
    draw_frame_counter += 1
    if draw_frame_counter == 10:
        draw_framerate = 10000 / (pygame.time.get_ticks() - draw_frame_counting_time)
        stutter_frequency = 1000 * stutter_counter / (pygame.time.get_ticks() - draw_frame_counting_time)
        draw_frame_counter = 0
        stutter_counter = 0
        draw_frame_counting_time = pygame.time.get_ticks()
    
    pygame.display.flip()
