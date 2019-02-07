from scalarfield import *
from fieldutils import HexMask

grid_a = 61
grid_b = 61
timescale = 1
simulation_frequency = 30 #in Hz
timestep = 1 / simulation_frequency

diffusivity = 3
density = ScalarHexField(grid_a, grid_b, mask = HexMask(grid_a, grid_b, True))
laplace = ScalarHexField(grid_a, grid_b, mask = density.mask)
insulation = HexMask(grid_a, grid_b, default = False)

def update_insulation(tile):
    if tile.a < 0 or tile.a >= grid_a or tile.b < 0 or tile.b >= grid_b:
        return
    if not density.valid_hex_v(tile):
        insulation.hexes[tile.a][tile.b] = False
        return
    for n in range(6):
        if not density.valid_hex_v(tile+dirs[n]):
            insulation.hexes[tile.a][tile.b] = True
            return
    insulation.hexes[tile.a][tile.b] = False

def update_insulation_all():
    for i in range(grid_a):
        for j in range(grid_b):
            if density.valid_hex(i,j):
                update_insulation(Vex(i,j))

update_insulation_all()

# heat equation woo
def simulate_step():
    cdef float c_timestep = timestep
    density.laplace(laplace) #This is where most time is spent
    for i in range(grid_a):
        for j in range(grid_b):
            if density.mask.hexes[i][j]:
                if insulation.hexes[i][j]:
                    summation = 0
                    count = 0
                    for n in range(6):
                        target = Vex(i,j) + dirs[n]
                        if density.valid_hex_v(target) and not insulation.hexes[target.a][target.b]:
                            summation += density.get_hex(target)
                            count += 1
                    if count > 0:
                        density.hexes[i][j] = summation / count
                else:
                    density.hexes[i][j] += laplace.hexes[i][j] * diffusivity * c_timestep