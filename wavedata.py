from scalarfield import *
from fieldutils import HexMask
import pygame

grid_a = 61
grid_b = 61

timescale = 1
simulation_frequency = 30 #in Hz
timestep = 1 / simulation_frequency

displacement = ScalarHexField(grid_a, grid_b, mask = HexMask(grid_a, grid_b, True))
velocity = ScalarHexField(grid_a, grid_b, mask = displacement.mask)
acceleration = ScalarHexField(grid_a, grid_b, mask = displacement.mask)
wave_speed = ScalarHexField(grid_a, grid_b, mask = displacement.mask, default_value = 9)
csquared = ScalarHexField(grid_a, grid_b, mask = displacement.mask, default_value = 81)

def simulate_step():
    displacement.evaluate_wave_equation(acceleration, csquared) #This is where most time is spent
    acceleration.add_fraction_to(velocity, timestep)
    velocity.add_fraction_to(displacement, timestep)