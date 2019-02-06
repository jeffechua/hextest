from scalarfield import *
from fieldutils import HexMask

grid_a = 61
grid_b = 61
timescale = 1
simulation_frequency = 30 #in Hz
timestep = 1 / simulation_frequency

density = ScalarHexField(grid_a, grid_b, mask = HexMask(grid_a, grid_b, True))
laplace = ScalarHexField(grid_a, grid_b, mask = density.mask)
diffusivity = ScalarHexField(grid_a, grid_b, mask = density.mask, default_value = 1)

# heat equation woo
def simulate_step():
    cdef float c_timestep = timestep
    density.laplace(laplace) #This is where most time is spent
    for i in range(grid_a):
        for j in range(grid_b):
            if density.mask.hexes[i][j]:
                density.hexes[i][j] += laplace.hexes[i][j] * diffusivity.hexes[i][j] * c_timestep