import math
from pygame import Vector2
from dataclasses import dataclass

# Useful constants
sin60 = math.sqrt(3)/2

# A Vex is a vector in a hexagonal basis with functions to interface with
# and convert between Cartesian vectors.
# Immutable to avoid accidents with copying and modification
@dataclass(frozen=True)
class Vex:

    a : int
    b : int

    # A number of useful operators and functions
    def x(self):                   return self.b - self.a / 2
    def y(self):                   return self.a * sin60
    def Vector2(self):             return Vector2(self.x(), self.y())
    def __add__(self, other):      return Vex(self.a + other.a, self.b + other.b)
    def __sub__(self, other):      return Vex(self.a - other.a, self.b - other.b)
    def __mul__(self,factor):      return Vex(self.a * factor, self.b * factor)
    def __rmul__(self,factor):     return Vex(self.a * factor, self.b * factor)
    def __truediv__(self, factor): return Vex(self.a / factor, self.b / factor)
    def __neg__ (self):            return Vex(-self.a, -self.b)
    def __abs__(self):             return math.sqrt(self.sqr_mag())
    def sqr_mag(self):             return self.x() * self.x() + self.y() * self.y()

    # This was surprisingly tricky - simply shearing back to a Cartesian basis
    # doesn't work, since that gives parallelograms instead of hexagonal "hitboxes"
    def round(self):

        a_floor = math.floor(self.a)
        b_floor = math.floor(self.b)
        trim_a = self.a - a_floor
        trim_b = self.b - b_floor
        trim = Vex(trim_a,trim_b)
        trim_x = trim.x()

        if trim_x < 0:
            if trim.sqr_mag() < (trim-dirs[0]).sqr_mag():
                return Vex(a_floor, b_floor)
            else:
                return Vex(a_floor, b_floor) + dirs[0]
        elif trim_x < 0.5:
            if trim.sqr_mag() < (trim-dirs[1]).sqr_mag():
                return Vex(a_floor, b_floor)
            else:
                return Vex(a_floor, b_floor) + dirs[1]
        else:
            if (trim-dirs[1]).sqr_mag() < (trim-dirs[2]).sqr_mag():
                return Vex(a_floor, b_floor) + dirs[1]
            else:
                return Vex(a_floor, b_floor) + dirs[2]

    # Finds the two hexagonal directions closest to the Vex and resolves it into them
    # Returns two tuples, each containing
    #  - The index of that resolved direction in the "dirs" array (bottom of file)
    #  - The magnitude in that direction
    def resolve_closest_axes(self):

        axes = 0  # Notating is if axes = n, closest directions are dir[n], dir[n+1]
        
        if self.b > 0:
            if self.a > 0:
                if self.a > self.b:
                    axes = 0
                else:
                    axes = 1
            else:
                axes = 2
        else:
            if self.a < 0:
                if self.a < self.b:
                    axes = 3
                else:
                    axes = 4
            else:
                axes = 5

        if axes == 0:
            return ((0, self.a - self.b), (1, self.b))
        elif axes == 1:
            return ((1, self.a), (2, self.b - self.a))
        elif axes == 2:
            return ((2, self.b), (3, -self.a))
        elif axes == 3:
            return ((3, -self.a + self.b),(4, -self.b))
        elif axes == 4:
            return ((4, -self.a), (5, -self.b + self.a))
        elif axes == 5:
            return ((5, -self.b), (0, self.a))

dirs = (Vex(1,0), Vex(1,1), Vex(0,1), Vex(-1,0), Vex(-1,-1), Vex(0,-1), Vex(1,0))
