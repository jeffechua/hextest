from hexvex import Vex, dirs
import math, fieldutils

class VectorHexField:

    def __init__(self, a, b, mask = None):
        self.a = a
        self.b = b
        self.maxima = []
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [None]*b
            for j in range(b):
                self.hexes[i][j] = Vex(0,0)
        if mask == None: self.mask = fieldutils.HexMask(a,b)
        else: self.mask = mask
    
    def getHex(self, vex):
        return self.hexes[vex.a][vex.b]

    def valid_hex_v(self, vex, ignore_mask = False):
        return self.valid_hex(vex.a, vex.b, ignore_mask)

    def valid_hex(self, a, b, ignore_mask = False):
        if a < 0 or a >= self.a or b<0 or b >= self.b:
            return False
        elif not self.mask.hexes[a][b] and not ignore_mask:
            return False
        return True

    def __iadd__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] += other.hexes[i][j]
        return self

    def __isub__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] -= other.hexes[i][j]
        return self

    def __imul__(self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] *= factor
        return self
                    
    def __itruediv__(self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] /= factor
        return self
                    
    def __neg__(self):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] = -self.hexes[i][j]
        return self
              
    def clear(self):
        self.maxima.clear()
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = Vex(0,0)
    
    def clone(self, other, multiplier = 1):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = other.hexes[i][j] * multiplier

    def apply_to(self, scalar_field, destination, step):
        destination.clone(scalar_field)
        for i in range(self.a):
            for j in range(self.b):
                if scalar_field.mask.hexes[i][j]:
                    resolution = self.hexes[i][j].resolve_closest_axes()
                    d1 = dirs[resolution[0][0]]
                    d2 = dirs[resolution[1][0]]
                    m1 = resolution[0][1] * step
                    m2 = resolution[1][1] * step
                    if m1+m2>scalar_field.hexes[i][j]:
                        f = scalar_field.hexes[i][j]/(m1+m2)
                        m1 *= f
                        m2 *= f
                    if scalar_field.validHex(i+d1.a, j+d1.b):
                        destination.hexes[i+d1.a][j+d1.b] += m1
                        destination.hexes[i][j] -= m1
                    if scalar_field.validHex(i+d2.a, j+d2.b):
                        destination.hexes[i+d2.a][j+d2.b] += m2
                        destination.hexes[i][j] -= m2
