from hexvex import Vex, dirs
import math

class HexMask:

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.hexes = [[False]*b] + [None]*(a-2) + [[False]*b]
        for i in range(1,a-1):
            self.hexes[i] = [False] + [True]*(b-2) + [False]

    def __iand__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.hexes[i][j] & other.hexes[i][j]

    def __ior__ (self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.hexes[i][j] | other.hexes[i][j]

    def __neg__ (self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = not self.hexes[i][j]

_mp_const = 3

class Monopole:

    def __init__(self, position, charge):
        self.position = position
        self.charge = charge
    
    def apply_to(self, potential_field):
        for i in range(potential_field.a):
            for j in range(potential_field.b):
                if potential_field.mask.hexes[i][j]:
                    potential_field.hexes[i][j] += _mp_const * self.charge / (_mp_const + abs(Vex(i,j)-self.position))

class Pipe:

    def __init__(self, origin, direction, length, radius, current):
        self.origin = origin
        self.direction = direction
        self.length = length
        self.radius = radius
        self.current = current

    """def apply_to(self, force_field):
        for w in range(-radius,radius):
            for i in range(0, self.length-math.abs(w)):
                pos = origin
                if force_field.valid(origin + )
                for j in range(1,radius):
"""

class VectorHexField:

    def __init__(self, a, b, mask = None):
        self.a = a
        self.b = b
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [None]*b
            for j in range(b):
                self.hexes[i][j] = Vex(0,0)
        if mask == None: self.mask = HexMask(a,b)
        else: self.mask = mask
    
    def getHex(self, vex):
        return self.hexes[vex.a][vex.b]

    def validHexV(self, vex):
        return self.validHex(vex.a, vex.b)

    def validHex(self, a, b):
        if a < 0 | a >= self.a | b<0 | b >= self.b:
            return False
        elif not self.mask.hexes[a][b]:
            return False
        return True

    def __iadd__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] += other.hexes[i][j]

    def __isub__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] -= other.hexes[i][j]

    def __imul__(self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] *= factor
                    
    def __itruediv__(self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] /= factor
                    
    def __neg__(self):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] = -self.hexes[i][j]
              
    def clear(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j]=0
    
    def clone(self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j]=other.hexes[i][j]

    def apply(self, scalar_field, destination):
        destination.clone(scalar_field)
        for i in range(self.a):
            for j in range(self.b):
                if scalar_field.mask.hexes[i][j]:
                    resolution = self.hexes[i][j].resolve_closest_axes
                    d1 = resolution[0][0]
                    d2 = resolution[1][0]
                    m1 = resolution[0][1]
                    m2 = resolution[1][1]
                    if m1+m2>scalar_field.hexes[i][j]:
                        f = scalar_field.hexes[i][j]/(m1+m2)
                        m1 *= f
                        m2 *= f
                    if scalar_field.mask.hexes[d1.x][d1.j]:
                        destination.hexes[i+d1.x][j+d1.j] += m1
                        destination.hexes[i][j] -= m1
                    if scalar_field.mask.hexes[d2.x][d2.j]:
                        destination.hexes[i+d2.x][j+d2.j] += m2
                        destination.hexes[i][j] -= m2

class ScalarHexField:

    def __init__(self, a, b, mask = None):
        self.a = a
        self.b = b
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [0]*b
        if mask == None: self.mask = HexMask(a,b)
        else: self.mask = mask

    def getHex(self, vex):
        return self.hexes[vex.a][vex.b]

    def validHexV(self, vex):
        return self.validHex(vex.a, vex.b)

    def validHex(self, a, b):
        if a < 0 | a >= self.a | b<0 | b >= self.b:
            return False
        elif not self.mask.hexes[a][b]:
            return False
        return True

    def __iadd__ (self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] += other.hexes[i][j]

    def __isub__ (self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] -= other.hexes[i][j]

    def __imul__ (self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] *= factor
                    
    def __itruediv__ (self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] /= factor
                    
    def __neg__ (self):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask[i][j]:
                    self.hexes[i][j] = -self.hexes[i][j]

    def grad(self):
        gradField = VectorHexField(self.a, self.b, self.mask)
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    for d in range(6):
                        k = i + dirs[d].a
                        l = j + dirs[d].b
                        if self.mask.hexes[k][l]:
                            gradField.hexes[i][j] += (self.hexes[k][l] - self.hexes[i][j]) * dirs[d]
        return gradField
                    
    def clear(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j]=0
    
    def clone(self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j]=other.hexes[i][j]