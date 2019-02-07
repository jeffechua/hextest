from hexvex import Vex, dirs
import math, fieldutils
from vectorfield import *
from collections import Sequence

class ScalarHexField:

    def __init__(self, a, b, mask = None, default_value = 0):
        self.hexes = [None]*a
        cdef int int_a = a 
        cdef int int_b = b #converting to cdef int gives ~5% performance improvement
        self.a = int_a
        self.b = int_b
        self.default_value = default_value
        cdef float float_default = default_value #gives a small 5-10% performance improvement
        for i in range(a):
            self.hexes[i] = [float_default]*b
        if mask == None: self.mask = fieldutils.HexMask(a,b)
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

    def add_fraction_to(self, destination, multiplier):
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    destination.hexes[i][j] += self.hexes[i][j] * multiplier

    def multiply_by_term(self, other):
        for i in range(self.a):
            for j in range(self.b):
                if other.mask.hexes[i][j] and self.mask.hexes[i][j]:
                    self.hexes[i][j] *= other.hexes[i][j]

    def sum(self):
        count = 0
        for i in range(self.a):
            for j in range(self.b):
                if self.mask.hexes[i][j]:
                    count += self.hexes[i][j]
        return count

    def grad(self, destination = None):
        gradField = destination
        if gradField == None:
            gradfield = VectorHexField(self.a, self.b, self.mask)
        else:
            gradField.clear()
        for i in range(self.a):
            for j in range(self.b):
                maximum = True
                if self.mask.hexes[i][j]:
                    for d in range(6):
                        k = i + dirs[d].a
                        l = j + dirs[d].b
                        if self.valid_hex(k,l):
                            delta = self.hexes[k][l] - self.hexes[i][j]
                            if delta > 0: maximum = False
                            gradField.hexes[i][j] += delta * dirs[d]
                if maximum: gradField.maxima.append(Vex(i,j))
        return gradField


    def dissolve_maxima(self, destination, vector_field, threshold, step):
        destination.clone(self)
        for maximum in vector_field.maxima:
            if vector_field.validHexV(maximum) and abs(vector_field.getHex(maximum)) < threshold:
                delta = [0] * 6
                for n in range(6):
                    if self.valid_hex_v(maximum + dirs[n]):
                        delta[n] = self.get_hex(maximum) - self.get_hex(maximum + dirs[n])
                sum = delta[0] + delta[1] + delta[2] + delta[3] + delta[4] + delta[5]
                if sum == 0: continue
                controller = 1 if sum < self.get_hex(maximum) else self.get_hex(maximum) / sum
                for n in range(6):
                    if delta[n] > 0:
                        destination.hexes[maximum.a+dirs[n].a][maximum.b+dirs[n].b] += delta[n] * controller * step
                        destination.hexes[maximum.a][maximum.b] -= delta[n] * controller * step
    
    #numerically evaluates the laplacian, which is written to [destination]
    def laplace(self, destination):
        magic_number = 1 + 2 / math.sqrt(3)
        # If we map c to y, we can geometrically approximate d2u/dx2 as (d2u/da2 + d2u/db2)/sqrt(3)
        # we can also change the x and y axes and blend b and c, or c and a,
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
        for i in range(self.a-1): #inteconnections between tiles on right edge
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

    #laplace, but ignores mask
    def laplace_indiscriminate(self, destination):
        magic_number = 1 + 2 / math.sqrt(3)
        # If we map c to y, we can geometrically approximate d2u/dx2 as (d2u/da2 + d2u/db2)/sqrt(3)
        # we can also change the x and y axes and blend b and c, or c and a,
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
                for n in range(3):
                    i2 = i + dirs[n].a
                    j2 = j + dirs[n].b
                    destination.hexes[i][j] += self.hexes[i2][j2]
                    destination.hexes[i2][j2] += self.hexes[i][j]
        for i in range(self.a-1): #inteconnections between tiles on right edge
            destination.hexes[i][self.b-1] += self.hexes[i+1][self.b-1]
            destination.hexes[i+1][self.b-1] += self.hexes[i][self.b-1]
        for j in range(self.b-1): #interconnections between tiles on left edge
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