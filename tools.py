from graphics_backend import *
import pygame
import math
from hexvex import Vex, dirs
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

    def select(self):
        pass

class FreeDrawTool(ToolBase):

    # each function takes a Vex as an argument - performs the "drawing" action on that tile
    def __init__(self, left_draw = none, right_draw = none):
        self.left_draw = left_draw
        self.right_draw = right_draw
        self.current_button = 0
        self.controlled_drag = False
        self.old_position = Vex(0,0) # -1 = left mouse, 0 = not drawing, 1 = right mouse
        ToolBase.__init__(self, mouse_down = self.begin_draw, mouse_up = self.end_draw, after_math = self.behave, after_draw = self.overlay_all)


    def select(self):
        self.controlled_drag = False


    def begin_draw(self, tile):
        self.old_position = tile
        self.controlled_drag = True


    def end_draw(self, tile):
        if self.controlled_drag and (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
            func = self.left_draw if self.current_button == -1 else self.right_draw
            for pos in self.get_all_traversed(tile):
                func(pos)
        self.old_position = tile
        self.controlled_drag = False


    def behave(self, tile):

        if pygame.mouse.get_pressed()[0]:
            self.current_button = -1
        elif pygame.mouse.get_pressed()[2]:
            self.current_button = 1
        else:
            self.current_button = 0
            return

        if pygame.key.get_pressed()[pygame.K_ESCAPE] or not pygame.mouse.get_focused():
            self.old_position = tile
            self.controlled_drag = False

        if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
            return
        
        func = self.left_draw if self.current_button == -1 else self.right_draw
        for pos in self.get_all_traversed(tile):
            func(pos)
        self.old_position = tile


    def overlay_all(self, tile):
        if self.controlled_drag and (pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]):
            for pos in self.get_all_traversed(tile):
                self.overlay_tile(pos)
    

    def overlay_tile(self, tile):
        screen.blit(get_hexagon((50,50,50)), hex_to_screen_space(tile) - half_hex, special_flags = pygame.BLEND_RGB_ADD)


    def get_all_traversed(self, tile):
        
        traversed = {tile}
        if key.get_pressed()[pygame.K_LSHIFT] or key.get_pressed()[pygame.K_LSHIFT]:
            for n in range(6):
                traversed.add(tile+dirs[n])
        
        dist = abs(tile - self.old_position)
        if dist > 0:
            dir = (tile - self.old_position)/dist / 3
            steps = math.floor(dist) * 3
            for n in range(steps):
                traversed.add((self.old_position + dir * n).round())
                if key.get_pressed()[pygame.K_LSHIFT] or key.get_pressed()[pygame.K_LSHIFT]:
                    for k in range(6):
                        traversed.add((self.old_position + dir * n).round() + dirs[k])

        return traversed