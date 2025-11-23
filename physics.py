# physics.py
from settings import *

class Physics:
    def __init__(self):
        self.gravity = GRAVITY
        self.friction = FRICTION
        self.min_y = GROUND_HORIZON
        self.max_y = WORLD_HEIGHT - 50

    def apply_gravity(self, entity):
        # Gravity affects Z axis (Height)
        if entity.z > 0 or entity.vz > 0:
            entity.vz -= self.gravity
            entity.is_grounded = False

    def apply_physics(self, entity):
        # Ground Movement (X/Y)
        entity.pos.x += entity.vel.x
        entity.pos.y += entity.vel.y
        
        # Height Movement (Z)
        entity.z += entity.vz
        
        # Friction
        entity.vel.x *= self.friction
        entity.vel.y *= self.friction
        
        # Floor Collision (Z-axis)
        if entity.z < 0:
            entity.z = 0
            entity.vz = 0
            entity.is_grounded = True
            
        # Screen Boundaries
        if entity.pos.x < 0: entity.pos.x = 0
        if entity.pos.x > WORLD_WIDTH - entity.rect.width: entity.pos.x = WORLD_WIDTH - entity.rect.width
        
        if entity.pos.y < self.min_y: entity.pos.y = self.min_y
        if entity.pos.y > WORLD_HEIGHT - entity.rect.height: entity.pos.y = WORLD_HEIGHT - entity.rect.height
        
        # Update Rect for drawing (Projected position)
        # We draw at (x, y - z)
        entity.rect.x = int(entity.pos.x)
        entity.rect.y = int(entity.pos.y - entity.z)
