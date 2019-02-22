import math
from hexvex import *
from collections import Sequence

# Essentially a hexagonal array of boolean values
class HexMask:

    #ONLY flag hexagonal if a = b
    def __init__(self, a, b, hexagonal = False, default = True):
        self.a = a
        self.b = b
        self.hexagonal = hexagonal
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [default]*b
        if hexagonal:
            halfway = math.floor(a/2)
            for i in range(halfway, a):
                for j in range(0, i-halfway):
                    self.hexes[i][j] = not default
                    self.hexes[j][i] = not default

    def __iand__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.hexes[i][j] and other.hexes[i][j]

    def __ior__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.hexes[i][j] or other.hexes[i][j]

    def __neg__(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = not self.hexes[i][j]

    def clear(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = True
        if self.hexagonal:
            halfway = math.floor(self.a/2)
            for i in range(halfway, self.a):
                for j in range(0, i-halfway):
                    self.hexes[i][j] = False
                    self.hexes[j][i] = False

# A hexagonal array of scalar values
cdef class ScalarHexField:

    cdef readonly int a
    cdef readonly int b
    cdef readonly float default_value
    cdef public list hexes
    cdef public object mask

    def __init__(self, a, b, mask = None, default_value = 0):
        self.hexes = [None]*a
        self.a = a
        self.b = b
        self.default_value = default_value
        for i in range(a):
            self.hexes[i] = [self.default_value]*b
        if mask == None: self.mask = HexMask(a,b)
        else: self.mask = mask

    def get_hex(self, vex):
        return self.hexes[vex.a][vex.b]

    def valid_hex_v(self, vex, ignore_mask = False):
        return self.valid_hex(vex.a, vex.b, ignore_mask)

    def valid_hex(self, a, b, ignore_mask = False):
        if a < 0 or a >= self.a or b<0 or b >= self.b:
            return False
        elif not self.mask.hexes[a][b] and not ignore_mask:
            return False
        return True

    def __iadd__ (self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] += other.hexes[i][j]
        return self

    def __isub__ (self, other):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] -= other.hexes[i][j]
        return self

    def __imul__ (self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] *= factor
        return self
                    
    def __itruediv__ (self, factor):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] /= factor
        return self
                    
    def __neg__ (self):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    self.hexes[i][j] = -self.hexes[i][j]
        return self

    def sum(self):
        count = 0
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    count += self.hexes[i][j]
        return count

    #numerically evaluates the laplacian, which is written to [destination]
    def laplace(self, destination):
        magic_number = 1 + 2 / math.sqrt(3)
        # If we map c to y, we can geometrically approximate d2u/dx2 as (d2u/da2 + d2u/db2)/sqrt(3)
        # we can also change the x and y axes and instead blend b and c, or c and a,
        # and if we average the (d2u/dx2 + d2u/dy2) obtained from all three axes picks we get
        #   (d2u/da2 + d2u/db2 + d3u/db2)*(1 + 2/(sqrt(3))
        # then we approximate d2u/da2 at p as:
        #   d2u/da2 = (u(p+a) - u(p)) - (u(p) - u(p-a)) = u(p+a) + u(p-a) - 2 u(p)
        # so we get
        #   (d2u/dx2 + d2u/dy2) = (u(p+a) + u(p-a) +
        #                          u(p+b) - u(p-b) +
        #                          u(p+c) - u(p-c) 
        #                        - 6 u(p)) * (1 + 2/(sqrt(3))
        destination.clone(self, -6)
        # Take care of most of the area
        for i in range(self.a-1):
            for j in range(self.b-1):
                if self.mask.hexes[i][j]: #We know we're not out of bounds so only checking the mask is faster
                    for n in range(3):
                        i2 = i + dirs[n].a
                        j2 = j + dirs[n].b
                        if self.mask.hexes[i2][j2]:
                            destination.hexes[i][j] += self.hexes[i2][j2]
                            destination.hexes[i2][j2] += self.hexes[i][j]
        for i in range(self.a-1): #interconnections between tiles on right edge
            if self.mask.hexes[i][self.b-1] and self.mask.hexes[i+1][self.b-1]:
                destination.hexes[i][self.b-1] += self.hexes[i+1][self.b-1]
                destination.hexes[i+1][self.b-1] += self.hexes[i][self.b-1]
        for j in range(self.b-1): #interconnections between tiles on left edge
            if self.mask.hexes[self.a-1][j] and self.mask.hexes[self.a-1][j+1]:
                destination.hexes[self.a-1][j] += self.hexes[self.a-1][j+1]
                destination.hexes[self.a-1][j+1] += self.hexes[self.a-1][j]
        for i in range(self.a):
            for j in range(self.b):
                destination.hexes[i][j] *= magic_number

    def clear(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = 0
    
    def reset(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.default_value

    def clone(self, other, multiplier = 1):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = other.hexes[i][j] * multiplier