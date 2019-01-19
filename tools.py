from graphics_backend import *
import pygame
import math

def none(tile): pass #empty function for if we don't want to define it

class ToolBase:

    # each function takes a Vex as an argument
    def __init__(self, mouse_down = none, mouse_up = none, before_math = none, after_math = none, after_draw = none):
        self.mouse_down = mouse_down
        self.mouse_up = mouse_up
        self.before_math = before_math
        self.after_math = after_math
        self.after_draw = after_draw

class FreeDrawTool(ToolBase):

    # each function takes a Vex as an argument - performs the "drawing" action on that tile
    def __init__(self, left_draw = none, right_draw = none):
        self.left_draw = left_draw
        self.right_draw = right_draw
        self.drawing = 0 # -1 = left mouse, 0 = not drawing, 1 = right mouse
        ToolBase.__init__(self, mouse_down = self.begin_draw, mouse_up = self.end_draw, after_math = self.behave)

    def begin_draw(self, tile):
        if pygame.mouse.get_pressed()[0]:
            self.drawing = -1
        if pygame.mouse.get_pressed()[2]:
            self.drawing = 1
        self.old_position = tile


    def end_draw(self, tile):
        self.drawing = 0

    def behave(self, tile):
        if self.drawing != 0:
            function = self.left_draw if self.drawing == -1 else self.right_draw
            dist = abs(tile - self.old_position)
            if dist > 0:
                dir = (tile - self.old_position)/dist / 2 # moving in unit length steps leaves holes. half-lengths is overkill,
                steps = math.floor(dist) * 2              # but then again this is far from being the performance bottleneck.
                for n in range(steps):
                    function((self.old_position + dir * n).round())
            function(tile)
            self.old_position = tile
            

    