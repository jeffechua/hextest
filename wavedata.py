from scalarfield import *
from fieldutils import HexMask

grid_a = 40
grid_b = 40

timescale = 1
simulation_frequency = 30
timestep = 1 / simulation_frequency
wave_speed = 10
csquared = wave_speed * wave_speed

displacement = ScalarHexField(grid_a, grid_b, mask = HexMask(grid_a, grid_b, True))
velocity = ScalarHexField(grid_a, grid_b, mask = displacement.mask)
acceleration = ScalarHexField(grid_a, grid_b, mask = displacement.mask)

def recalculate():
    displacement.evaluate_wave_equation(acceleration, csquared)
    acceleration.add_fraction_to(velocity, timestep)
    velocity.add_fraction_to(displacement, timestep)