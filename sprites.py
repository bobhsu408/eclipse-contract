# sprites.py
import pygame
import random
from settings import *
vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.z = 0
        self.vz = 0
        
        self.speed = 2.5
        self.max_speed = 5
        self.jump_force = 8
        self.is_grounded = True
        self.soul = 100
        self.facing_right = True
        
        # Try loading custom image
        try:
            self.original_image = pygame.image.load("assets/player.png").convert_alpha()
            self.image = self.original_image
            self.rect = self.image.get_rect()
            self.using_custom_art = True
            print("Loaded custom player art.")
        except FileNotFoundError:
            # Fallback to procedural
            self.image = pygame.Surface((50, 70), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.using_custom_art = False
            self.render_visuals()
        
    def render_visuals(self):
        if self.using_custom_art: return
        
        self.image.fill((0,0,0,0)) # Clear
        
        # Colors
        ROBE_COLOR = (75, 0, 130) # Indigo
        HOOD_COLOR = (48, 25, 52) # Dark Purple
        SKIN_COLOR = (20, 20, 20) # Shadowy
        EYE_COLOR = (0, 255, 255) # Cyan Glow
        
        # Draw Robe (Triangle-ish)
        pygame.draw.polygon(self.image, ROBE_COLOR, [(10, 70), (40, 70), (35, 20), (15, 20)])
        pygame.draw.circle(self.image, HOOD_COLOR, (25, 20), 15)
        pygame.draw.circle(self.image, SKIN_COLOR, (25, 22), 8)
        
        eye_offset = 2 if self.facing_right else -2
        pygame.draw.circle(self.image, EYE_COLOR, (25 + eye_offset + 3, 22), 2)
        pygame.draw.circle(self.image, EYE_COLOR, (25 + eye_offset - 3, 22), 2)
        
        staff_x = 45 if self.facing_right else 5
        pygame.draw.line(self.image, (139, 69, 19), (staff_x, 70), (staff_x, 10), 3)
        pygame.draw.circle(self.image, (148, 0, 211), (staff_x, 10), 5)

    def update(self, physics):
        keys = pygame.key.get_pressed()
        
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x = -1
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x = 1
            self.facing_right = True
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y = 1
            
        if move_x != 0 or move_y != 0:
            input_vec = vec(move_x, move_y).normalize()
            self.vel += input_vec * self.speed
        
        # Visual Update
        if self.using_custom_art:
            if self.facing_right:
                self.image = self.original_image
            else:
                self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.render_visuals()

        # Clamp Speed
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        
        physics.apply_gravity(self)
        physics.apply_physics(self)
        
    def jump(self):
        if self.is_grounded:
            self.vz = self.jump_force
            self.is_grounded = False

    def draw_shadow(self, surface, camera_offset):
        # Draw shadow at ground position
        shadow_rect = pygame.Rect(0, 0, 40, 12)
        shadow_rect.centerx = int(self.pos.x + 25) # Center of sprite width (50)
        shadow_rect.centery = int(self.pos.y + 70 - 5)
        
        # Apply camera
        final_rect = shadow_rect.move(camera_offset)
        
        s = pygame.Surface((40, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 0, 40, 12))
        surface.blit(s, final_rect)

class Ghoul(pygame.sprite.Sprite):
    def __init__(self, x, y, ai_type="follow", ai_params=None):
        super().__init__()
        
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.z = 0
        self.vz = 0
        
        self.speed = 1.5 + random.uniform(-0.2, 0.2)
        self.is_grounded = True
        self.facing_right = random.choice([True, False])
        
        # Try loading custom image
        try:
            self.original_image = pygame.image.load("assets/ghoul.png").convert_alpha()
            self.image = self.original_image
            self.rect = self.image.get_rect()
            self.using_custom_art = True
        except FileNotFoundError:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.using_custom_art = False
            self.render_visuals()
        
        # AI System
        from ai import create_ai
        ai_params = ai_params or {}
        self.ai = create_ai(ai_type, self, **ai_params)
        
    def render_visuals(self):
        if self.using_custom_art: return
        
        self.image.fill((0,0,0,0))
        
        BODY_COLOR = (85, 107, 47) # Olive Drab
        DARK_COLOR = (40, 50, 20)
        EYE_COLOR = (255, 50, 50) # Red
        
        pygame.draw.ellipse(self.image, BODY_COLOR, (5, 10, 30, 25))
        
        head_x = 25 if self.facing_right else 5
        pygame.draw.circle(self.image, BODY_COLOR, (head_x + 5, 15), 10)
        
        eye_x = head_x + 8 if self.facing_right else head_x + 2
        pygame.draw.circle(self.image, EYE_COLOR, (eye_x, 13), 2)
        
        arm_start = (20, 20)
        arm_end = (35, 25) if self.facing_right else (5, 25)
        pygame.draw.line(self.image, DARK_COLOR, arm_start, arm_end, 3)

    def update(self, physics, player, enemies=None):
        # 使用 AI 系統來決定行為
        self.ai.update(physics, player, enemies)
        
        # 更新視覺
        if self.using_custom_art:
            if self.facing_right:
                self.image = self.original_image
            else:
                self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.render_visuals()
            
        physics.apply_gravity(self)
        physics.apply_physics(self)
        
    def draw_shadow(self, surface, camera_offset):
        shadow_rect = pygame.Rect(0, 0, 30, 8)
        shadow_rect.centerx = int(self.pos.x + 20)
        shadow_rect.centery = int(self.pos.y + 40 - 5)
        
        final_rect = shadow_rect.move(camera_offset)
        
        s = pygame.Surface((30, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 80), (0, 0, 30, 8))
        surface.blit(s, final_rect)
