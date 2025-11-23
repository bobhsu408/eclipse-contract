# camera.py
import pygame
from settings import *

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Return a rect moved by the camera offset
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)
        
    def apply_pos(self, pos):
        return pos + pygame.math.Vector2(self.camera.x, self.camera.y)

    def update(self, target):
        # Center camera on target
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # Limit scrolling to map size
        x = min(0, max(x, -(self.width - SCREEN_WIDTH)))
        y = min(0, max(y, -(self.height - SCREEN_HEIGHT)))
        
        self.camera = pygame.Rect(x, y, self.width, self.height)
