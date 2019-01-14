import math
import pygame
from dataclasses import dataclass

sin60 = math.sqrt(3)/2

@dataclass(frozen=True)
class Vex:

    a : int
    b : int

    def x(self):
        return self.b - self.a / 2

    def y(self):
        return self.a * sin60

    def __add__(self, other):
        return Vex(self.a + other.a, self.b + other.b)
    
    def __sub__(self, other):
        return Vex(self.a - other.a, self.b - other.b)

    def __mul__(self,factor):
        return Vex(self.a * factor, self.b * factor)
    
    def __rmul__(self,factor):
        return Vex(self.a * factor, self.b * factor)
    
    def __truediv__(self, factor):
        return Vex(self.a / factor, self.b / factor)

    def __neg__ (self):
        return Vex(-self.a, -self.b)
    
    def __abs__(self):
        return math.sqrt(self.x() * self.x() + self.y() * self.y())

    def resolve_closest_axes (self):

        axes = 0
        """If axes = n, then the closest directions are dir[n] and dir[n+1]"""
        
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

        print("nothing whould have reached here!")

global dirs
dirs = (Vex(1,0), Vex(1,1), Vex(0,1), Vex(-1,0), Vex(-1,-1), Vex(0,-1), Vex(1,0))