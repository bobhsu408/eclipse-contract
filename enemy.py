# enemy.py
"""
敵人系統
包含基礎敵人類別和不同類型的敵人
"""
import pygame
import random
from settings import *

class Enemy(pygame.sprite.Sprite):
    """基礎敵人類別"""
    def __init__(self, x, y, enemy_type="skeleton"):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.z = 0  # Height for 2.5D
        self.vz = 0
        self.is_grounded = True
        
        # Stats
        self.enemy_type = enemy_type
        self.max_hp = 50
        self.hp = self.max_hp
        self.speed = 1.0
        self.damage = 10
        self.attack_range = 30
        self.attack_cooldown = 60  # frames
        self.attack_timer = 0
        
        # AI State
        self.state = "patrol"  # patrol, chase, attack, hurt, dead
        self.target = None
        self.patrol_point_a = pygame.math.Vector2(x - 100, y)
        self.patrol_point_b = pygame.math.Vector2(x + 100, y)
        self.patrol_target = self.patrol_point_b
        
        # Detection
        self.detection_range = 200
        self.lose_target_range = 300
        
        # Visual
        self.facing_right = True
        self.create_image()
        self.rect = self.image.get_rect()
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Animation
        self.hurt_timer = 0
        self.death_timer = 0
        
    def create_image(self):
        """創建敵人圖像（程式化繪製）"""
        size = 40
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if self.enemy_type == "skeleton":
            # 骷髏 - 灰白色
            # Body
            pygame.draw.rect(self.image, (200, 200, 200), (15, 20, 10, 15))
            # Head
            pygame.draw.rect(self.image, (220, 220, 220), (12, 10, 16, 12))
            # Eyes
            pygame.draw.circle(self.image, (255, 0, 0), (17, 15), 2)
            pygame.draw.circle(self.image, (255, 0, 0), (23, 15), 2)
            # Arms
            pygame.draw.rect(self.image, (180, 180, 180), (10, 22, 5, 10))
            pygame.draw.rect(self.image, (180, 180, 180), (25, 22, 5, 10))
            # Weapon (sword)
            pygame.draw.rect(self.image, (150, 150, 150), (30, 18, 8, 2))
            
        elif self.enemy_type == "goblin":
            # 哥布林 - 綠色
            # Body
            pygame.draw.ellipse(self.image, (80, 120, 60), (12, 18, 16, 18))
            # Head
            pygame.draw.circle(self.image, (90, 130, 70), (20, 15), 8)
            # Eyes
            pygame.draw.circle(self.image, (255, 255, 0), (17, 14), 2)
            pygame.draw.circle(self.image, (255, 255, 0), (23, 14), 2)
            # Ears
            pygame.draw.polygon(self.image, (70, 110, 50), [(12, 12), (8, 8), (12, 16)])
            pygame.draw.polygon(self.image, (70, 110, 50), [(28, 12), (32, 8), (28, 16)])
            
    def update(self, physics, player, units):
        """更新敵人狀態"""
        if self.state == "dead":
            self.death_timer += 1
            if self.death_timer > 60:  # 1 second
                self.kill()  # Remove from sprite group
            return
        
        # Update timers
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        
        # AI Logic
        self.ai_update(player, units)
        
        # Physics
        physics.apply_gravity(self)
        physics.apply_physics(self)
        
        # Update rect
        self.rect.center = (int(self.pos.x), int(self.pos.y - self.z))
        
        # Flip image based on direction
        if self.vel.x > 0:
            self.facing_right = True
        elif self.vel.x < 0:
            self.facing_right = False
    
    def ai_update(self, player, units):
        """AI 行為邏輯"""
        # Check for targets (player        # Find closest target (weighted by threat)
        potential_targets = [player] + units
        closest_target = None
        best_score = float('inf')
        
        for target in potential_targets:
            if hasattr(target, 'hp') and target.hp > 0:
                dist = self.pos.distance_to(target.pos)
                threat = getattr(target, 'threat', 1)
                # Lower score = higher priority
                # Higher threat and closer distance = lower score
                score = dist / max(threat, 1)  # Divide distance by threat
                if score < best_score:
                    best_score = score
                    closest_target = target
                    closest_dist = dist
        
        # State Machine
        if self.state == "patrol":
            # Patrol between two points
            if self.pos.distance_to(self.patrol_target) < 10:
                # Switch patrol target
                if self.patrol_target == self.patrol_point_a:
                    self.patrol_target = self.patrol_point_b
                else:
                    self.patrol_target = self.patrol_point_a
            
            # Move towards patrol target
            direction = (self.patrol_target - self.pos).normalize() if self.pos.distance_to(self.patrol_target) > 0 else pygame.math.Vector2(0, 0)
            self.vel = direction * self.speed * 0.5  # Slower when patrolling
            
            # Check for targets in range
            if closest_target and closest_dist < self.detection_range:
                self.state = "chase"
                self.target = closest_target
        
        elif self.state == "chase":
            if not self.target or not hasattr(self.target, 'hp') or self.target.hp <= 0:
                self.state = "patrol"
                self.target = None
                return
            
            dist_to_target = self.pos.distance_to(self.target.pos)
            
            # Lost target
            if dist_to_target > self.lose_target_range:
                self.state = "patrol"
                self.target = None
                return
            
            # In attack range
            if dist_to_target < self.attack_range:
                if self.attack_timer == 0:
                    self.state = "prepare_attack"
                    self.vz = 5  # Jump
                    self.is_grounded = False
                    self.vel = pygame.math.Vector2(0, 0) # Stop moving while jumping
                else:
                    self.state = "attack_cooldown" # Wait for cooldown
                    self.vel = pygame.math.Vector2(0, 0)
                return
            
            # Chase target (Omnidirectional)
            direction = (self.target.pos - self.pos).normalize()
            self.vel = direction * self.speed
        
        elif self.state == "prepare_attack":
            # Wait until grounded
            if self.z <= 0 and self.vz <= 0: # Landed
                self.perform_attack()
                self.state = "attack_cooldown"
                self.attack_timer = self.attack_cooldown
        
        elif self.state == "attack_cooldown":
            if self.attack_timer == 0:
                self.state = "chase"
            else:
                # Face target while waiting
                if self.target:
                    if self.target.pos.x > self.pos.x:
                        self.facing_right = True
                    else:
                        self.facing_right = False
        
        elif self.state == "attack":
            # Legacy state, redirect to chase
            self.state = "chase"
        
        elif self.state == "hurt":
            # Knockback effect
            self.vel *= 0.9
            if self.hurt_timer == 0:
                self.state = "chase" if self.target else "patrol"
    
    def perform_attack(self):
        """執行攻擊"""
        if self.target and hasattr(self.target, 'take_damage'):
            # Check if still in range
            if self.pos.distance_to(self.target.pos) < self.attack_range:
                self.target.take_damage(self.damage)
                print(f"{self.enemy_type} attacked for {self.damage} damage!")
    
    def take_damage(self, amount):
        """受到傷害"""
        self.hp -= amount
        self.hurt_timer = 10  # 10 frames of hurt state
        
        if self.hp <= 0:
            self.hp = 0
            self.state = "dead"
            print(f"{self.enemy_type} defeated!")
        else:
            self.state = "hurt"
            # Knockback
            if self.target:
                knockback_dir = (self.pos - self.target.pos).normalize()
                self.vel = knockback_dir * 3
    
    def draw_shadow(self, surface, cam_offset):
        """繪製陰影"""
        # Shadow is always on the ground (y), not affected by z
        shadow_x = int(self.pos.x + cam_offset[0])
        shadow_y = int(self.pos.y + cam_offset[1])
        
        # Draw shadow centered at feet
        shadow_rect = pygame.Rect(0, 0, 30, 10)
        shadow_rect.center = (shadow_x, shadow_y)
        
        s = pygame.Surface((30, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 100), (0, 0, 30, 10))
        surface.blit(s, shadow_rect)
        
        # Debug: Draw attack range
        # self.draw_attack_range(surface, cam_offset)

    def draw_attack_range(self, surface, cam_offset):
        """繪製攻擊範圍（除錯用）"""
        range_surf = pygame.Surface((self.attack_range * 2, self.attack_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surf, (255, 0, 0, 50), (self.attack_range, self.attack_range), self.attack_range)
        
        # Use rect center which is already updated with position and z-height
        # rect.center is in world coordinates (but projected to 2D)
        # We need to subtract camera offset
        
        screen_center_x = self.rect.centerx + cam_offset[0]
        screen_center_y = self.rect.centery + cam_offset[1]
        
        surface.blit(range_surf, (screen_center_x - self.attack_range, screen_center_y - self.attack_range))

    def draw_hp_bar(self, surface, cam_offset):
        """繪製生命條"""
        if self.hp >= self.max_hp:
            return  # Don't show HP bar if full health
        
        bar_width = 40
        bar_height = 4
        
        # Position above head
        # pos.y is feet, z is height. Subtract height and some offset for head.
        bar_x = int(self.pos.x + cam_offset[0] - bar_width // 2)
        bar_y = int(self.pos.y - self.z + cam_offset[1] - 50)
        
        # Background (red)
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health (green)
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)


class Skeleton(Enemy):
    """骷髏戰士 - 基礎近戰敵人"""
    def __init__(self, x, y):
        super().__init__(x, y, "skeleton")
        self.max_hp = 50
        self.hp = self.max_hp
        self.speed = 1.2
        self.damage = 10
        self.attack_range = 35


class Goblin(Enemy):
    """哥布林 - 快速但脆弱"""
    def __init__(self, x, y):
        super().__init__(x, y, "goblin")
        self.max_hp = 30
        self.hp = self.max_hp
        self.speed = 2.0
        self.damage = 8
        self.attack_range = 30
        self.attack_cooldown = 45  # Faster attack
