from scalarfield import *
from fieldutils import HexMask

grid_a = 61
grid_b = 61
timescale = 1
simulation_frequency = 30 #in Hz
timestep = 1 / simulation_frequency

displacement = ScalarHexField(grid_a, grid_b, mask = HexMask(grid_a, grid_b, True))
velocity = ScalarHexField(grid_a, grid_b, mask = displacement.mask)
acceleration = ScalarHexField(grid_a, grid_b, mask = displacement.mask)
damping = ScalarHexField(grid_a, grid_b, mask = displacement.mask)
damp_multiplier = ScalarHexField(grid_a, grid_b, mask = damping.mask, default_value = 1)
wave_speed = ScalarHexField(grid_a, grid_b, mask = displacement.mask, default_value = 9)
csquared = ScalarHexField(grid_a, grid_b, mask = displacement.mask, default_value = 81)

def simulate_step():
    cdef float c_timestep = timestep
    displacement.evaluate_wave_equation(acceleration, csquared) #This is where most time is spent
    for i in range(grid_a):            # Checking displacement mask *does* slightly increase performance for hexagonal grids
        for j in range(grid_b):        # However, masking damping and not multiplying by damp_multiplier if undamped actually *decreases* performance
            if displacement.mask.hexes[i][j]: # Yes, even if literally the entire map is undamped
                velocity.hexes[i][j] = velocity.hexes[i][j] * damp_multiplier.hexes[i][j] + acceleration.hexes[i][j] * c_timestep
                displacement.hexes[i][j] += velocity.hexes[i][j] * c_timestep