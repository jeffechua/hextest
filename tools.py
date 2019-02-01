from graphics_backend import *
import pygame
import math
from hexvex import Vex, dirs
from pygame import key

def none(arg): pass #empty function for if we don't want to define it

def controlling():
    return pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]
def shifting():
    return pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]
        

class ToolBase:

    # each function takes a Vex as an argument
    def __init__(self, mouse_down = none, mouse_up = none, mouse_scroll = none, before_math = none, after_math = none, after_draw = none):
        self.mouse_down = mouse_down
        self.mouse_up = mouse_up
        self.mouse_scroll = mouse_scroll
        self.before_math = before_math
        self.after_math = after_math
        self.after_draw = after_draw

    def select(self):
        pass

def parallelogram_spanning(p1, p2):
    edges = (p2 - p1).resolve_closest_axes()
    for i in range(edges[0][1]+1):    # reminder: the each element of "edges" is a tuple of a unit vector, and a magnitude
        for j in range(edges[1][1]+1): # the unit vector is passed as its index in hexvex.dirs, not as a hexvex.Vex object
            yield p1 + i * hexvex.dirs[edges[0][0]] + j * hexvex.dirs[edges[1][0]]

class FreeDrawTool(ToolBase):

    # each function takes a Vex as an argument - performs the "drawing" action on that tile
    def __init__(self, left_draw = none, right_draw = none):
        self.left_draw = left_draw
        self.right_draw = right_draw
        self.current_button = 0
        self.brush_radius = 1
        self.cont_drag = False
        self.old_position = Vex(0,0) # -1 = left mouse, 0 = not drawing, 1 = right mouse
        ToolBase.__init__(self, mouse_down = self.begin_draw, mouse_up = self.end_draw,
                          mouse_scroll = self.change_brush_size, after_math = self.behave, after_draw = self.overlay_selected)


    def select(self):
        self.cont_drag = False


    def begin_draw(self, tile):
        self.old_position = tile
        self.cont_drag = True


    def end_draw(self, tile):
        func = self.left_draw if self.current_button == -1 else self.right_draw
        if self.cont_drag:
            if controlling():
                for pos in self.get_all_traversed(tile):
                    func(pos)
            elif shifting():
                for pos in parallelogram_spanning(self.old_position, tile):
                    func(pos)
        self.old_position = tile
        self.cont_drag = False

    
    def change_brush_size(self, delta):
        self.brush_radius = clamp(self.brush_radius + delta, 0, 10)


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
            self.cont_drag = False

        if controlling() or shifting():
            return
        
        func = self.left_draw if self.current_button == -1 else self.right_draw
        for pos in self.get_all_traversed(tile):
            func(pos)
        self.old_position = tile


    def overlay_selected(self, tile):
        r = self.brush_radius
        w = hex_width*(2*r+1)
        h = hex_height*(2*r+1) #Todo: fix; this is more than necessary
        brush = pygame.Surface((w, h))
        brush.set_colorkey((0,0,0))
        for i in range(-r, r+1):                       # This makes sense if you
            for j in range(clamp(i-r, -r, 0), clamp(i+r, 0, r)+1): # draw it out
                points = list()
                for k in range(6):
                    points.append(p2[k] + Vex(i,j).Vector2() * cell_parameter + (w/2, h/2))
                pygame.draw.polygon(brush, (50,50,50), points)
        if self.cont_drag:
            if controlling():
                axis = self.get_traversal_axis(tile)
                overlay = pygame.Surface(screen.get_size())
                for pos in axis:
                    overlay.blit(brush, hex_to_screen_space(pos) - (w/2, h/2))
                screen.blit(overlay, (0,0), special_flags = pygame.BLEND_RGB_ADD)
            elif shifting():
                overlay = pygame.Surface(screen.get_size())
                screen.blit(overlay, (0,0), special_flags = pygame.BLEND_RGB_ADD)
                params = (tile - self.old_position).resolve_closest_axes()
                for pos in parallelogram_spanning(self.old_position, tile):
                    c = hex_to_screen_space(pos)
                    points = list()
                    for k in range(6):
                        points.append(c + p2[k])
                    pygame.draw.polygon(overlay, (50,50,50), points)
                screen.blit(overlay, (0,0), special_flags = pygame.BLEND_RGB_ADD)
        else:
            if shifting():
                draw_combine_back_hexagon(hex_to_screen_space(tile), (50,50,50), flags = pygame.BLEND_RGB_ADD)
            else:
                screen.blit(brush, hex_to_screen_space(tile) - (w/2, h/2), special_flags = pygame.BLEND_RGB_ADD)

    def get_traversal_axis(self, tile):
        axis = {tile}
        dist = abs(tile - self.old_position)
        if dist > 0.0:
            dir = (tile - self.old_position)/dist / 3
            steps = round(dist) * 3
            for n in range(steps):
                axis.add((self.old_position + dir * n).round())
        return axis

    def get_all_traversed(self, tile):
        axis = self.get_traversal_axis(tile)
        traversed = set()
        r = self.brush_radius
        for point in axis:
            for i in range(-r, r+1):                       # This makes sense if you
                for j in range(clamp(i-r, -r, 0), clamp(i+r, 0, r)+1): # draw it out
                    traversed.add(point + Vex(i, j))

        return traversed

