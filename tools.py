from graphics_backend import *
import pygame
import math
from hexvex import dirs
from pygame import key

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

        if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
            return

        button = ""
        if pygame.mouse.get_pressed()[0]:
            button = -1
        elif pygame.mouse.get_pressed()[2]:
            button = 1
        else:
            return
        
        function = self.left_draw if button == -1 else self.right_draw
        dist = abs(tile - self.old_position)
        if dist > 0:
            dir = (tile - self.old_position)/dist / 3 # moving in unit length steps leaves holes. third-lengths is overkill,
            steps = math.floor(dist) * 3              # but then again this is far from being the performance bottleneck.
            for n in range(steps):
                function((self.old_position + dir * n).round())
                if key.get_pressed()[pygame.K_LSHIFT] or key.get_pressed()[pygame.K_LSHIFT]:
                    for k in range(6):
                        function((self.old_position + dir * n).round() + dirs[k])
        function(tile)
        if key.get_pressed()[pygame.K_LSHIFT] or key.get_pressed()[pygame.K_LSHIFT]:
            for n in range(6):
                function(tile+dirs[n])
        self.old_position = tile
            

    