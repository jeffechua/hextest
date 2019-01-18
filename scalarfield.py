from hexvex import Vex, dirs
import math, fieldutils

class ScalarHexField:

    def __init__(self, a, b, mask = None, default_value = 0):
        self.a = a
        self.b = b
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [default_value]*b
        if mask == None: self.mask = fieldutils.HexMask(a,b)
        else: self.mask = mask

    def getHex(self, vex):
        return self.hexes[vex.a][vex.b]

    def validHexV(self, vex):
        return self.validHex(vex.a, vex.b)

    def validHex(self, a, b):
        if a < 0 or a >= self.a or b<0 or b >= self.b:
            return False
        elif not self.mask.hexes[a][b]:
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

    def grad(self, destination = None):
        gradField = destination
        if gradField == None:
            VectorHexField(self.a, self.b, self.mask)
        else:
            gradField.clear()
        for i in range(self.a):
            for j in range(self.b):
                maximum = True
                if self.mask.hexes[i][j]:
                    for d in range(6):
                        k = i + dirs[d].a
                        l = j + dirs[d].b
                        if self.validHex(k,l):
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
                    if self.validHexV(maximum + dirs[n]):
                        delta[n] = self.getHex(maximum) - self.getHex(maximum + dirs[n])
                sum = delta[0] + delta[1] + delta[2] + delta[3] + delta[4] + delta[5]
                if sum == 0: continue
                controller = 1 if sum < self.getHex(maximum) else self.getHex(maximum) / sum
                for n in range(6):
                    if delta[n] > 0:
                        destination.hexes[maximum.a+dirs[n].a][maximum.b+dirs[n].b] += delta[n] * controller * step
                        destination.hexes[maximum.a][maximum.b] -= delta[n] * controller * step
    
    #numerically evaluates the wave equation for d2u/dt2, which is written to [destination]
    def evaluate_wave_equation(self, destination, csquared):
        magic_number = 1 + 2 / math.sqrt(3)
        for i in range(self.a):
            for j in range(self.b):
                if self.validHex(i,j):
                    # here we geometrically approximate d2u/dx2 as (d2u/da2 + d2u/db2)/sqrt(3)
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
                    sum = -6 * self.hexes[i][j]
                    for n in range(6):
                        if self.validHex(i + dirs[n].a, j + dirs[n].b):
                            sum += self.hexes[i + dirs[n].a][j + dirs[n].b]
                    sum *= magic_number
                    destination.hexes[i][j] = sum * csquared



    def clear(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = 0
    
    def clone(self, other, multiplier = 1):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = other.hexes[i][j] * multiplier