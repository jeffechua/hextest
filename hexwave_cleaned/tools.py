from graphics import *
import pygame
import math
from hexvex import Vex, dirs
from pygame import key


# Utility functions to check if control or shift is held
def controlling():
    return pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]
def shifting():
    return pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]
        
# Utility iterator returning tiles in the smallest parallelogram that spans two points.
# Used for the zone selection mode (SHIFT and drag)
def parallelogram_spanning(p1, unit_hex):
    edges = (unit_hex - p1).resolve_closest_axes()
    for i in range(edges[0][1]+1):     # reminder: each element of "edges" is a tuple of a unit vector and a magnitude
        for j in range(edges[1][1]+1): # the unit vector is passed as its index in hexvex.dirs, not as a hexvex.Vex object
            yield p1 + i * dirs[edges[0][0]] + j * dirs[edges[1][0]]


# Simple toolbar class that manages and displays a list of icons and tools
# icons should be 50x50
class Toolbar:

    def __init__(self, icons, tools):
        self.icons = icons
        self.tools = tools
        self.current = 0
        self.len = len(self.tools)
        free_drawing()
        for n in range(self.len):
            pygame.draw.rect(screen, (20,20,20), pygame.Rect(10,10 + 80*n,60,60))
            screen.blit(self.icons[n], (15, 80*n+15))
        self.select(0)
        restrict_drawing()
    
    def select(self, index):
        free_drawing()
        pygame.draw.rect(screen, (20,20,20), pygame.Rect(10,10 + 80 * self.current,60,60))
        screen.blit(self.icons[self.current], (15, 80 * self.current + 15))
        self.current = index
        if self.current >= self.len: self.current = 0
        elif self.current < 0:       self.current = self.len - 1
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(10,10 + 80 * self.current,60,60))
        screen.blit(self.icons[self.current], (15, 80 * self.current + 15))
        self.tools[self.current].select()
        restrict_drawing()

    def increment_selection(self):
        self.select(self.current+1)

    def decrement_selection(self):
        self.select(self.current-1)


def none(arg0 = None, arg1 = None, arg2 = None): pass #empty function for if we don't want to define it

# Abstract base class from which tools are derived
class ToolBase:

    # Each argument is a function takes a Vex (tile currently moused over) and returns nothing,
    # except mouse_scroll which takes a number (scroll amount) and returns nothing.
    # They are called directly from the main loop.
    def __init__(self, mouse_down = none, mouse_up = none, mouse_scroll = none, before_math = none, after_math = none, after_draw = none):
        self.mouse_down = mouse_down
        self.mouse_up = mouse_up
        self.mouse_scroll = mouse_scroll
        self.before_math = before_math
        self.after_math = after_math
        self.after_draw = after_draw

    # The action function are passed in the constructor since they're different for each tool
    # but the set-up procedure for select() should be the same for all tools of the same type
    def select(self):
        pass


class FreeDrawTool(ToolBase):

    # each function takes a Vex as an argument - performs the "drawing" action on that tile
    def __init__(self, left_draw = none, right_draw = none):
        self.left_draw = left_draw
        self.right_draw = right_draw
        self.current_button = 0
        self.brush_radius = 1
        self.dragging = False
        self.old_position = Vex(0,0) # -1 = left mouse, 0 = not drawing, 1 = right mouse
        ToolBase.__init__(self, mouse_down = self.begin_draw, mouse_up = self.end_draw,
                          mouse_scroll = self.change_brush_size, after_math = self.behave, after_draw = self.overlay_selected)

    def select(self):
        self.dragging = False

    def begin_draw(self, tile):
        self.old_position = tile
        self.dragging = True

    def end_draw(self, tile):
        func = self.left_draw if self.current_button == -1 else self.right_draw
        # only do things at end_draw if the user is dragging; if not dragging all
        # actions will have been handled in behave()
        if self.dragging:
            if controlling():
                for pos in self.get_all_traversed(tile):
                    func(pos)
            elif shifting():
                for pos in parallelogram_spanning(self.old_position, tile):
                    func(pos)
        self.old_position = tile
        self.dragging = False

    def change_brush_size(self, delta):
        self.brush_radius = clamp(self.brush_radius + delta, 0, 10)

    def behave(self, tile):
        
        # Update if user is using the left or right mouse button
        if pygame.mouse.get_pressed()[0]:
            self.current_button = -1
        elif pygame.mouse.get_pressed()[2]:
            self.current_button = 1
        else:
            self.current_button = 0
            return # Everything past this point assumes user is dragging (mouse is down!)

        # Cancel drag if user escapes or window loses focus
        if pygame.key.get_pressed()[pygame.K_ESCAPE] or not pygame.mouse.get_focused():
            self.old_position = tile
            self.dragging = False

        # Return if shifting or controlling - handle these special drags in 
        if controlling() or shifting():
            return
        
        # If we're still here, the user is dragging but not shifting or controlling
        # so we just do the action on all tiles passed over
        func = self.left_draw if self.current_button == -1 else self.right_draw
        for pos in self.get_all_traversed(tile):
            func(pos)
        self.old_position = tile

    def overlay_selected(self, tile):

        # Holding shift, i.e. selecting a zone, is treated a special case
        if shifting():
            if self.dragging:
                overlay = pygame.Surface(screen.get_size())
                params = (tile - self.old_position).resolve_closest_axes()
                for pos in parallelogram_spanning(self.old_position, tile):
                    c = hex_to_screen_space(pos)
                    points = list(map(lambda v : v + c, unit_hex))
                    pygame.draw.polygon(overlay, (50,50,50), points)
                screen.blit(overlay, (0,0), special_flags = pygame.BLEND_RGB_ADD)
            else:
                blend_hexagon(hex_to_screen_space(tile), (50,50,50), flags = pygame.BLEND_RGB_ADD)
            return # special case handled, so abort function

        # Create a hexagonal brush template to blit onto screen
        r = self.brush_radius  # radius
        w = hex_width*(2*r+1)  # brush width
        h = hex_height*(2*r+1) # brush height
        brush = pygame.Surface((w, h))
        brush.set_colorkey((0,0,0))
        # Fill the brush template by iterating through every cell in the brush area
        # We can't just draw one big hexagon since the edges are "jagged"
        for i in range(-r, r+1): 
            for j in range(clamp(i-r, -r, 0), clamp(i+r, 0, r)+1):
                points = list(map(lambda v : v + Vex(i,j).Vector2() * cell_parameter + (w/2, h/2), unit_hex))
                pygame.draw.polygon(brush, (50,50,50), points)
        
        # if user is draggin with CTRL down, i.e. drawing a line, blit the brush all across the line axis
        if self.dragging and controlling():     
            axis = self.get_traversal_axis(tile)
            overlay = pygame.Surface(screen.get_size())
            for pos in axis:
                overlay.blit(brush, hex_to_screen_space(pos) - (w/2, h/2))
            screen.blit(overlay, (0,0), special_flags = pygame.BLEND_RGB_ADD)
        # otherwise, just blit the brush on the cursor
        else:
            screen.blit(brush, hex_to_screen_space(tile) - (w/2, h/2), special_flags = pygame.BLEND_RGB_ADD)

    # Gets the set of points intersecting a line from the start selection tile to the currently selected tile
    def get_traversal_axis(self, tile):
        axis = {tile}
        dist = abs(tile - self.old_position)
        if dist > 0.0:
            dir = (tile - self.old_position)/dist / 3
            steps = round(dist) * 3
            for n in range(steps):
                axis.add((self.old_position + dir * n).round())
        return axis

    # Gets all tiles within brush radius of the points obtained in get_traversal_axis
    def get_all_traversed(self, tile):
        axis = self.get_traversal_axis(tile)
        traversed = set()
        r = self.brush_radius
        for point in axis:
            for i in range(-r, r+1):                       # This makes sense if you
                for j in range(clamp(i-r, -r, 0), clamp(i+r, 0, r)+1): # draw it out
                    traversed.add(point + Vex(i, j))

        return traversed


class SetValueDrawTool(FreeDrawTool):

    # unlike FreeDrawTool, SetValueDrawTool (obviously) also passes the current value setting to left_draw and right_draw
    # which is why we need a wrapper to adapt the left_draw and right_draw functionality of FreeDrawTool
    def __init__(self, read_source, default_value, minval, maxval, interval, left_draw = none, right_draw = none):
        self.read_source = read_source
        self.value = default_value
        self.min = minval
        self.max = maxval
        self.interval = interval
        self.numbers = list()

        # Pre-generate text that we might need to blit to the screen
        for n in range(minval, maxval+interval, interval):
            rendered = font.render(str(n), (255,255,255), size = hex_width)
            self.numbers.append((rendered[0], pygame.Vector2(rendered[1].w/2, rendered[1].h/2)))

        self.left_draw_raw = left_draw
        self.right_draw_raw = right_draw
        
        FreeDrawTool.__init__(self, self.left_draw_wrapper, self.right_draw_wrapper)
        self.mouse_scroll = self.scroll

    # middleman functions to inject the "current value" information
    def left_draw_wrapper(self, tile): 
        self.left_draw_raw(tile, self.value)
    def right_draw_wrapper(self, tile):
        self.right_draw_raw(tile, self.value)

    def scroll(self, delta):
        if controlling():
            self.change_brush_size(delta)
        else:
            self.value = clamp(self.value + self.interval * delta, self.min, self.max)

    def overlay_selected(self, tile):
        # Most functionality just inherits from FreeDrawTool
        FreeDrawTool.overlay_selected(self, tile)

        # But we also want to display the values of every cell
        for i in range(self.read_source.a):
            for j in range(self.read_source.b):
                if self.read_source.mask.hexes[i][j]:
                    text = self.numbers[round((self.read_source.hexes[i][j]-self.min)/self.interval)]
                    screen.blit(text[0], hex_to_screen_space(Vex(i,j)) - text[1])

        # And also show what value is selected by the player next to the cursor
        mouse_surf = font.render(str(self.value), (0,0,0), (255,255,255), size = 40 if shifting() else 20)
        pos = pygame.mouse.get_pos()
        screen.blit(mouse_surf[0], (pos[0] - mouse_surf[1].w, pos[1] - mouse_surf[1].h))
