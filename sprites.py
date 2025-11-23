# sprites.py
import pygame
import random
import math
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
        self.max_soul = 100
        self.soul = 50 # Start with half soul
        self.facing_right = True
        
        # Combat stats
        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 15
        self.attack_range = 40
        self.attack_cooldown = 30
        self.attack_timer = 0
        self.invincible_timer = 0  # Invincibility frames after being hit
        self.threat = 1  # Low threat - enemies prefer attacking summons
        
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
        # Update timers
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        
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
    
    def take_damage(self, amount):
        """受到傷害"""
        if self.invincible_timer > 0:
            return  # Still invincible
        
        self.hp -= amount
        self.invincible_timer = 60  # 1 second of invincibility
        
        if self.hp <= 0:
            self.hp = 0
            print("Player defeated!")
            # TODO: Game over logic
        else:
            print(f"Player took {amount} damage! HP: {self.hp}/{self.max_hp}")
    
    def attack(self, enemies):
        """攻擊敵人"""
        if self.attack_timer > 0:
            return False
        
        # Find enemies in range
        for enemy in enemies:
            if hasattr(enemy, 'take_damage'):
                dist = self.pos.distance_to(enemy.pos)
                if dist < self.attack_range:
                    # Check if enemy is in front of player
                    is_in_front = (enemy.pos.x > self.pos.x) if self.facing_right else (enemy.pos.x < self.pos.x)
                    if is_in_front:
                        enemy.take_damage(self.damage)
                        self.attack_timer = self.attack_cooldown
                        return True
        
        return False

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

class MagicMissile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_pos):
        super().__init__()
        self.pos = vec(x, y)
        self.z = 10  # Lowered height
        
        # Calculate velocity
        direction = (target_pos - self.pos).normalize()
        self.vel = direction * 8  # Speed
        
        self.damage = 10
        self.max_distance = 300
        self.distance_traveled = 0
        
        # Visuals
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 255, 255), (5, 5), 5)
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self, physics=None): # physics arg for compatibility
        self.pos += self.vel
        self.distance_traveled += self.vel.length()
        
        if self.distance_traveled > self.max_distance:
            self.kill()
            
        # Update rect
        self.rect.center = (int(self.pos.x), int(self.pos.y - self.z))

    def draw_shadow(self, surface, camera_offset):
        # Small shadow
        shadow_x = int(self.pos.x + camera_offset[0])
        shadow_y = int(self.pos.y + camera_offset[1])
        s = pygame.Surface((10, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 50), (0, 0, 10, 4))
        surface.blit(s, (shadow_x - 5, shadow_y - 2))

class Loot(pygame.sprite.Sprite):
    def __init__(self, x, y, loot_type="gold", value=10):
        super().__init__()
        self.pos = vec(x, y)
        self.z = 20 # Start slightly in air
        self.vel = vec(random.uniform(-2, 2), random.uniform(-2, 2))
        self.vz = random.uniform(3, 6) # Pop up
        
        self.loot_type = loot_type
        self.value = value
        self.is_collected = False
        
        # Visuals
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        if loot_type == "gold":
            pygame.draw.circle(self.image, (255, 215, 0), (6, 6), 5) # Gold
            pygame.draw.circle(self.image, (255, 255, 200), (4, 4), 2) # Shine
        else: # Soul
            pygame.draw.circle(self.image, (100, 200, 255), (6, 6), 5) # Blue
            
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    def update(self, physics, player):
        if self.is_collected:
            # Fly towards player UI (simplified: just kill)
            self.kill()
            return

        # Magnet effect
        dist = self.pos.distance_to(player.pos)
        if dist < 100:
            direction = (player.pos - self.pos).normalize()
            self.vel += direction * 0.5
            
        # Physics
        physics.apply_gravity(self)
        physics.apply_physics(self)
        
        # Bounce
        if self.z <= 0 and abs(self.vz) > 1:
            self.vz *= -0.6 # Bounce
            self.vel *= 0.8 # Friction
            
        self.rect.center = (int(self.pos.x), int(self.pos.y - self.z))
        
    def draw_shadow(self, surface, camera_offset):
        shadow_x = int(self.pos.x + camera_offset[0])
        shadow_y = int(self.pos.y + camera_offset[1])
        s = pygame.Surface((10, 4), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 50), (0, 0, 10, 4))
        surface.blit(s, (shadow_x - 5, shadow_y - 2))

class Ghoul(pygame.sprite.Sprite):
    def __init__(self, x, y, ai_type="commandable", ai_params=None):
        super().__init__()
        
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.z = 0
        self.vz = 0
        
        self.speed = 1.0 + random.uniform(-0.1, 0.1)
        self.threat = 5  # Threat value for enemy targeting
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
        
        # Combat stats
        self.max_hp = 40
        self.hp = self.max_hp
        self.damage = 8
        self.attack_range = 35
        self.attack_cooldown = 40
        self.attack_timer = 0
        
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

    def update(self, physics, player, enemies=None, game=None):
        # Update timers
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
        # 使用 AI 系統來決定行為
        self.ai.update(physics, player, enemies)
        
        # Auto attack
        if enemies and self.attack_timer == 0:
            closest = min(enemies, key=lambda e: self.pos.distance_to(e.pos))
            if self.pos.distance_to(closest.pos) < self.attack_range:
                self.attack(closest)
        
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
    
    def take_damage(self, amount):
        """受到傷害"""
        self.hp -= amount
        
        if self.hp <= 0:
            self.hp = 0
            self.kill()  # Remove from sprite group
            print("Ghoul defeated!")
        else:
            print(f"Ghoul took {amount} damage! HP: {self.hp}/{self.max_hp}")
    
    def attack(self, target):
        """攻擊目標"""
        if self.attack_timer > 0:
            return False
        
        if hasattr(target, 'take_damage'):
            dist = self.pos.distance_to(target.pos)
            if dist < self.attack_range:
                target.take_damage(self.damage)
                self.attack_timer = self.attack_cooldown
                return True
        
        return False
        
    def draw_shadow(self, surface, camera_offset):
        shadow_rect = pygame.Rect(0, 0, 30, 8)
        shadow_rect.centerx = int(self.pos.x + 20)
        shadow_rect.centery = int(self.pos.y + 40 - 5)
        
        final_rect = shadow_rect.move(camera_offset)
        
        s = pygame.Surface((30, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 80), (0, 0, 30, 8))
        surface.blit(s, final_rect)

class Wisp(pygame.sprite.Sprite):
    def __init__(self, x, y, ai_type="commandable", ai_params=None):
        super().__init__()
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.z = 40 # Hover height
        self.vz = 0
        
        self.speed = 1.2
        self.threat = 3  # Lower threat than melee units
        self.is_grounded = False
        self.facing_right = True
        
        # Visuals
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 255, 255), (10, 10), 8) # Core
        pygame.draw.circle(self.image, (100, 255, 255, 100), (10, 10), 12) # Glow
        self.rect = self.image.get_rect()
        
        # AI
        from ai import create_ai
        ai_params = ai_params or {}
        self.ai = create_ai(ai_type, self, **ai_params)
        
        # Stats
        self.max_hp = 20
        self.hp = self.max_hp
        self.damage = 5
        self.attack_range = 150
        self.attack_cooldown = 50
        self.attack_timer = 0
        
    def update(self, physics, player, enemies=None, game=None):
        if self.attack_timer > 0:
            self.attack_timer -= 1
            
        self.ai.update(physics, player, enemies)
        
        # Hover effect
        self.z = 40 + math.sin(pygame.time.get_ticks() * 0.005) * 5
        self.vz = 0 # Ignore gravity
        
        # Auto attack
        if enemies and self.attack_timer == 0 and game:
            closest = min(enemies, key=lambda e: self.pos.distance_to(e.pos))
            if self.pos.distance_to(closest.pos) < self.attack_range:
                self.attack(closest, game)
                
        physics.apply_physics(self)
        
    def attack(self, target, game):
        missile = MagicMissile(self.pos.x, self.pos.y, target.pos)
        missile.z = self.z # Fire from current height
        missile.damage = self.damage
        game.projectiles.add(missile)
        game.all_sprites.add(missile)
        self.attack_timer = self.attack_cooldown
        
    def draw_shadow(self, surface, camera_offset):
        shadow_rect = pygame.Rect(0, 0, 20, 6)
        shadow_rect.centerx = int(self.pos.x)
        shadow_rect.centery = int(self.pos.y)
        final_rect = shadow_rect.move(camera_offset)
        s = pygame.Surface((20, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 50), (0, 0, 20, 6))
        surface.blit(s, final_rect)
        
    def take_damage(self, amount):
        """受到傷害"""
        self.hp -= amount
        
        if self.hp <= 0:
            self.hp = 0
            self.kill()
            print("Wisp defeated!")
        else:
            print(f"Wisp took {amount} damage! HP: {self.hp}/{self.max_hp}")
