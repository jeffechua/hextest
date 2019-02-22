from hexvex import *
from hexfields import *

grid_a = 61
grid_b = 61
timescale = 1
simulation_frequency = 30 #in Hz
timestep = 1 / simulation_frequency

mask            = HexMask(grid_a, grid_b, hexagonal = True)
displacement    = ScalarHexField(grid_a, grid_b, mask = mask)
velocity        = ScalarHexField(grid_a, grid_b, mask = mask)
laplace         = ScalarHexField(grid_a, grid_b, mask = mask)
damping         = ScalarHexField(grid_a, grid_b, mask = mask)
damp_multiplier = ScalarHexField(grid_a, grid_b, mask = mask, default_value = 1)
wave_speed      = ScalarHexField(grid_a, grid_b, mask = mask, default_value = 9)
csquared        = ScalarHexField(grid_a, grid_b, mask = mask, default_value = 81)

def simulate_step():
    cdef float c_timestep = timestep
    displacement.laplace(laplace)             # This calculation is where most time is spent
    for i in range(grid_a):                   # Checking displacement mask *does* slightly increase performance for hexagonal grids
        for j in range(grid_b):               # However, masking damping and not multiplying by damp_multiplier if undamped actually
            if displacement.mask.hexes[i][j]: # *decreases* performance, even if the entire map is undamped
                velocity.hexes[i][j] = velocity.hexes[i][j] * damp_multiplier.hexes[i][j] + \
                                       laplace.hexes[i][j] * csquared.hexes[i][j] * c_timestep
                displacement.hexes[i][j] += velocity.hexes[i][j] * c_timestep