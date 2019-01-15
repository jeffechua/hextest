from hexvex import *
from hexfield import *
import pygame
from pygame import Vector2

hex_radius = 25
hex_height = 2 * hex_radius
hex_width = 2 * hex_radius * sin60

cell_parameter = hex_width

padding = 0.15

pygame.init()
screen = pygame.display.set_mode((800, 600))
done = False
clock = pygame.time.Clock()

hexagon = pygame.Surface((hex_width, hex_height))
hexagon.set_colorkey((0,0,0))
center = pygame.math.Vector2(hex_width / 2, hex_height / 2)
p = [None]*6
p[0] = Vector2(0, (hex_height - hex_radius) / 2)
p[1] = Vector2(0, (hex_height + hex_radius) / 2)
p[2] = Vector2(hex_width/2, hex_height)
p[3] = Vector2(hex_width, (hex_height+hex_radius)/2)
p[4] = Vector2(hex_width, (hex_height-hex_radius)/2)
p[5] = Vector2(hex_width/2, 0)
for point in p:
    point += (center - point)*(padding)
pygame.draw.polygon(hexagon, (255, 255, 255), p)

grid_a = 7
grid_b = 7

origin_position = Vex(0, grid_a / 2)

for i in range(grid_a):
    for j in range(grid_b):
        position = origin_position + Vex(i, j)
        screen.blit(hexagon, position.Vector2()*cell_parameter)


while not done:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    done = True
    
    pygame.display.flip()