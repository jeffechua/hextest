from scalarfield import *
from fieldutils import HexMask

grid_a = 61
grid_b = 61
timescale = 0.5
simulation_frequency = 30 #in Hz
simulation_timestep = 1 / simulation_frequency
real_timestep = 1 / simulation_frequency / timescale

class Numbers:
    def __init__(self):
        self.net_mass = 0
        self.target_net_mass = 0
        self.laplace_sum = 0

numbers = Numbers()
diffusivity = 3
density = ScalarHexField(grid_a, grid_b, mask = HexMask(grid_a, grid_b, True))
laplace = ScalarHexField(grid_a, grid_b, mask = density.mask)
insulation = HexMask(grid_a, grid_b, default = False)

def update_insulation(tile):
    if tile.a < 0 or tile.a >= grid_a or tile.b < 0 or tile.b >= grid_b:
        return
    border = tile.a == 0 or tile.b == 0 or tile.a == grid_a - 1 or tile.b == grid_b - 1
    if (not density.mask.hexes[tile.a][tile.b]) or border: # if border or masked
        for n in range(6):                         
            if density.valid_hex_v(tile+dirs[n]) and not insulation.hexes[tile.a][tile.b]:  # and has an adjacent unmasked and conducting cell
                insulation.hexes[tile.a][tile.b] = True #it is insulating
                return
    insulation.hexes[tile.a][tile.b] = False

def update_insulation_all():
    for i in range(grid_a):
        for j in range(grid_b):
            update_insulation(Vex(i,j))

update_insulation_all()

# heat equation woo
def simulate_step():
    cdef float c_timestep = simulation_timestep
    density.laplace_indiscriminate(laplace) #This is where most time is spent
    numbers.net_mass = density.sum()
    numbers.laplace_sum = 0
    for i in range(1,grid_a-1):
        for j in range(1,grid_b-1):
            if density.mask.hexes[i][j]: # these conditions exclude insulators and void
                numbers.laplace_sum += laplace.hexes[i][j]
    if numbers.laplace_sum == 0: return
    numbers.laplace_sum *= diffusivity * c_timestep
    cdef float correction = numbers.target_net_mass / (numbers.laplace_sum + numbers.net_mass)
    for i in range(grid_a):
        for j in range(grid_b):
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
            elif density.mask.hexes[i][j]:
                density.hexes[i][j] = (density.hexes[i][j] + laplace.hexes[i][j] * diffusivity * c_timestep) * correction