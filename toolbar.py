from graphics_backend import *
import pygame

class Toolbar:

    # icons should be 50x50
    def __init__(self, icons, tools):
        self.icons = icons
        self.tools = tools
        self.current = 0
        self.len = len(self.tools)
        for n in range(self.len):
            pygame.draw.rect(screen, (20,20,20), pygame.Rect(10,10 + 80*n,60,60))
            screen.blit(self.icons[n], (15, 80*n+15))
        self.select(0)
    
    def select(self, index):
        pygame.draw.rect(screen, (20,20,20), pygame.Rect(10,10 + 80 * self.current,60,60))
        screen.blit(self.icons[self.current], (15, 80 * self.current + 15))
        self.current = index
        if self.current >= self.len: self.current = 0
        elif self.current < 0:       self.current = self.len - 1
        pygame.draw.rect(screen, (255,255,255), pygame.Rect(10,10 + 80 * self.current,60,60))
        screen.blit(self.icons[self.current], (15, 80 * self.current + 15))

    def increment_selection(self):
        self.select(self.current+1)

    def decrement_selection(self):
        self.select(self.current-1)