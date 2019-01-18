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

class Pulse:
    
    def __init__(self, steps, amplitude):
        self.steps = steps
        self.remaining_steps = steps
        self.amplitude = amplitude
    
    def next(self):
        self.remaining_steps -= 1
        if self.remaining_steps == 0:
            return -999
        return math.sin(self.remaining_steps / self.steps * math.pi) * self.amplitude