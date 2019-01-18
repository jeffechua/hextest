from hexvex import Vex, dirs
import math

class HexMask:

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [True]*b

    def __iand__(self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.hexes[i][j] and other.hexes[i][j]

    def __ior__ (self, other):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = self.hexes[i][j] or other.hexes[i][j]

    def __neg__ (self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = not self.hexes[i][j]

_mp_const = 3

class Monopole:

    def __init__(self, position, charge, field, on_changed):
        self.__position = position
        self.__charge = charge
        self.on_changed = on_changed
        self.__field = None
        self.field = field

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, new_pos):
        if self.field != None:
            Monopole.apply(-self.charge, self.position, self.field)
            self.__position += new_pos
            Monopole.apply(self.charge, self.position, self.field)
            self.on_changed()
        else:
            self.__position += new_pos
    
    @property
    def charge(self):
        return self.__charge

    @charge.setter
    def charge(self, new_charge):
        if self.field != None:
            Monopole.apply(new_charge - self.charge, self.position, self.field)
            self.__charge += pos
            self.on_changed()
        else:
            self.__charge += pos
    
    @property
    def field(self):
        return self.__field
    
    @field.setter
    def field(self, new_field):
        if self.field != None:
            Monopole.apply(-self.charge, self.position, self.field)
        self.__field = new_field
        if self.field != None:
            Monopole.apply(self.charge, self.position, self.field)
        self.on_changed()

    @staticmethod
    def apply(charge, position, potential_field):
        for i in range(potential_field.a):
            for j in range(potential_field.b):
                if potential_field.mask.hexes[i][j]:
                    potential_field.hexes[i][j] += _mp_const * charge / (_mp_const + abs(Vex(i,j)-position))

    def __del__(self):
        if self.field != None:
            Monopole.apply(-self.charge, self.position, self.field)
        self.on_changed()


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
        self.minima = []
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
        if a < 0 or a >= self.a or b<0 or b >= self.b:
            return False
        elif not self.mask.hexes[a][b]:
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
        self.minima.clear()
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


class ScalarHexField:

    def __init__(self, a, b, mask = None, default_value = 0):
        self.a = a
        self.b = b
        self.hexes = [None]*a
        for i in range(a):
            self.hexes[i] = [default_value]*b
        if mask == None: self.mask = HexMask(a,b)
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

    def grad(self, destination = None):
        gradField = destination
        if gradField == None:
            VectorHexField(self.a, self.b, self.mask)
        else:
            gradField.clear()
        for i in range(self.a):
            for j in range(self.b):
                minimum = True
                if self.mask.hexes[i][j]:
                    for d in range(6):
                        k = i + dirs[d].a
                        l = j + dirs[d].b
                        if self.validHex(k,l):
                            delta = self.hexes[k][l] - self.hexes[i][j]
                            if delta > 0: minimum = False
                            gradField.hexes[i][j] += delta * dirs[d]
                if minimum: gradField.minima.append(Vex(i,j))
        return gradField
    
    def dissolve_maxima(self, destination, vector_field, threshold, step):
        destination.clone(self)
        for i in range(self.a):
            for j in range(self.b):
                if vector_field.validHex(i,j) and abs(vector_field.hexes[i][j]) < threshold:
                    delta = [0] * 6
                    maximum = True
                    for n in range(6):
                        if self.validHex(i+dirs[n].a, j+dirs[n].b):
                            delta[n] = self.hexes[i][j] - self.hexes[i+dirs[n].a][j+dirs[n].b]
                            if delta[n] <= 0: maximum = False
                    if not maximum: continue
                    sum = delta[0] + delta[1] + delta[2] + delta[3] + delta[4] + delta[5]
                    controller = 1 if sum < self.hexes[i][j] else self.hexes[i][j] / sum
                    for n in range(6):
                        if delta[n] > 0:
                            destination.hexes[i+dirs[n].a][j+dirs[n].b] += delta[n] * controller * step
                            destination.hexes[i][j] -= delta[n] * controller * step
                    
    def clear(self):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = 0
    
    def clone(self, other, multiplier = 1):
        for i in range(self.a):
            for j in range(self.b):
                self.hexes[i][j] = other.hexes[i][j] * multiplier