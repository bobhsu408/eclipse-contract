# main.py
import pygame
import sys
import math
import random
from settings import *
from physics import Physics
from sprites import Player, Ghoul, MagicMissile, Loot, Wisp
from camera import Camera
from particles import ParticleSystem
from menu import show_main_menu
from enemy import Skeleton, Goblin
from ui import SummonUI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        
        self.running = True
        self.physics = Physics()
        self.camera = Camera(WORLD_WIDTH, WORLD_HEIGHT)
        self.particles = ParticleSystem()
        
        self.player = Player(100, 300)
        self.units = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.loot = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
        self.ui = SummonUI(self)
        
        # Game State
        self.gold = 0
        self.target_gold = 100
        self.respawn_queue = [] # (time, x, y, type)
        # Exit covers the right side of the map, from horizon to bottom
        self.exit_rect = pygame.Rect(WORLD_WIDTH - 100, GROUND_HORIZON, 100, WORLD_HEIGHT - GROUND_HORIZON)
        
        # Spawn some test enemies
        self.spawn_enemy(400, 300, "skeleton")
        self.spawn_enemy(600, 300, "goblin")
        self.spawn_enemy(800, 300, "skeleton")
    
    def spawn_enemy(self, x, y, enemy_type="skeleton"):
        """生成敵人"""
        if enemy_type == "skeleton":
            enemy = Skeleton(x, y)
        elif enemy_type == "goblin":
            enemy = Goblin(x, y)
        else:
            enemy = Skeleton(x, y)
        
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        
    def spawn_loot(self, x, y):
        """生成掉落物"""
        # Random loot
        count = random.randint(1, 3)
        for _ in range(count):
            loot_type = "gold" if random.random() > 0.2 else "soul"
            val = 10 if loot_type == "gold" else 5
            loot = Loot(x, y, loot_type, val)
            self.loot.add(loot)
            self.all_sprites.add(loot)
            
    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # UI Events
            self.ui.handle_event(event)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Check if UI handled it? 
                    # Ideally UI returns True if handled.
                    # But handle_event returns None currently unless I check return value.
                    # Let's check if mouse is in UI area?
                    # UI is at bottom.
                    if pygame.mouse.get_pos()[1] > SCREEN_HEIGHT - 100:
                        continue
                        
                    # Convert screen pos to world pos
                    mx, my = pygame.mouse.get_pos()
                    cam_x, cam_y = self.camera.camera.topleft
                    world_x = mx - cam_x
                    world_y = my - cam_y
                    target_pos = pygame.math.Vector2(world_x, world_y)
                    
                    # Check cooldown
                    if self.player.attack_timer == 0:
                        missile = MagicMissile(self.player.pos.x, self.player.pos.y - 35, target_pos)
                        self.projectiles.add(missile)
                        self.all_sprites.add(missile)
                        self.player.attack_timer = 20 # Cooldown
                        print("Fired Magic Missile!")
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                
                if event.key == pygame.K_e:
                    # Check exit
                    if self.gold >= self.target_gold:
                        if self.exit_rect.colliderect(self.player.rect):
                            print("Level Complete!")
                            self.running = False # End game for now (or show victory screen)
                        
    def update(self):
        self.player.update(self.physics)
        
        # Track enemies to detect death
        enemies_before = set(self.enemies)
        
        # Update units (pass enemies list and game)
        enemies_list = list(self.enemies)
        for unit in self.units:
            unit.update(self.physics, self.player, enemies_list, self)
        
        # Update enemies (pass player and units)
        units_list = list(self.units)
        for enemy in self.enemies:
            enemy.update(self.physics, self.player, units_list)
            
        # Detect deaths
        enemies_after = set(self.enemies)
        dead_enemies = enemies_before - enemies_after
        for enemy in dead_enemies:
            self.spawn_loot(enemy.pos.x, enemy.pos.y)
            # Queue respawn (5 seconds = 5000ms)
            respawn_time = pygame.time.get_ticks() + 5000
            self.respawn_queue.append((respawn_time, enemy.pos.x, enemy.pos.y, enemy.enemy_type))
            
        # Process Respawn Queue
        current_time = pygame.time.get_ticks()
        # Filter queue: keep items that are not yet ready
        # We need to iterate carefully to remove items
        remaining_respawns = []
        for item in self.respawn_queue:
            r_time, r_x, r_y, r_type = item
            if current_time >= r_time:
                self.spawn_enemy(r_x, r_y, r_type)
                self.particles.emit_summon_effect(r_x, r_y) # Effect for spawn
            else:
                remaining_respawns.append(item)
        self.respawn_queue = remaining_respawns
            
        # Update projectiles
        self.projectiles.update()
        
        # Update Loot
        for item in self.loot:
            item.update(self.physics, self.player)
            # Collection check
            if item.pos.distance_to(self.player.pos) < 30:
                if item.loot_type == "gold":
                    self.gold += item.value
                else:
                    if self.player.soul < self.player.max_soul:
                        self.player.soul += item.value
                        if self.player.soul > self.player.max_soul:
                            self.player.soul = self.player.max_soul
                item.kill()
                print(f"Collected {item.loot_type}! Gold: {self.gold}, Soul: {self.player.soul}")
        
        # Projectile collisions
        for missile in self.projectiles:
            # Check collision with enemies
            hits = pygame.sprite.spritecollide(missile, self.enemies, False)
            for enemy in hits:
                # Check Z-height (simple check)
                if abs(enemy.z - missile.z) < 30:
                    enemy.take_damage(missile.damage)
                    missile.kill()
                    self.particles.emit_summon_effect(enemy.pos.x, enemy.pos.y) # Reuse effect for hit
                    break
        
        self.particles.update()
        self.camera.update(self.player)
            
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # Camera Offset
        cam_offset = self.camera.camera.topleft
        
        # Draw Floor
        floor_rect = pygame.Rect(0, GROUND_HORIZON, WORLD_WIDTH, WORLD_HEIGHT - GROUND_HORIZON)
        pygame.draw.rect(self.screen, COLOR_GROUND, self.camera.apply_rect(floor_rect))
        
        # Draw Grid (Subtle Runic Feel - Darker)
        grid_size = 100
        for x in range(0, WORLD_WIDTH, grid_size):
            start = self.camera.apply_pos(pygame.math.Vector2(x, 0))
            end = self.camera.apply_pos(pygame.math.Vector2(x, WORLD_HEIGHT))
            pygame.draw.line(self.screen, (20, 20, 25), start, end)
            
        for y in range(0, WORLD_HEIGHT, grid_size):
            start = self.camera.apply_pos(pygame.math.Vector2(0, y))
            end = self.camera.apply_pos(pygame.math.Vector2(WORLD_WIDTH, y))
            pygame.draw.line(self.screen, (20, 20, 25), start, end)

        # Draw Horizon Line
        start = self.camera.apply_pos(pygame.math.Vector2(0, GROUND_HORIZON))
        end = self.camera.apply_pos(pygame.math.Vector2(WORLD_WIDTH, GROUND_HORIZON))
        pygame.draw.line(self.screen, (50, 0, 50), start, end, 2)
        
        # Draw Exit
        exit_screen_rect = self.camera.apply_rect(self.exit_rect)
        if self.gold >= self.target_gold:
            # Active Exit
            pygame.draw.rect(self.screen, (0, 255, 0), exit_screen_rect, 2)
            # Draw "EXIT" text
            text = self.font.render("EXIT (Press E)", True, (0, 255, 0))
            self.screen.blit(text, (exit_screen_rect.centerx - 40, exit_screen_rect.top - 20))
        else:
            # Inactive Exit
            pygame.draw.rect(self.screen, (100, 100, 100), exit_screen_rect, 2)
            text = self.font.render(f"Need {self.target_gold} Gold", True, (150, 150, 150))
            self.screen.blit(text, (exit_screen_rect.centerx - 50, exit_screen_rect.top - 20))
        
        # Draw World Border
        border_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)
        pygame.draw.rect(self.screen, (100, 0, 0), self.camera.apply_rect(border_rect), 2)
        
        # Draw Shadows
        for sprite in self.all_sprites:
            if hasattr(sprite, 'draw_shadow'):
                sprite.draw_shadow(self.screen, cam_offset)
        
        # Sort sprites by Y for depth
        sprites_list = self.all_sprites.sprites()
        sprites_list.sort(key=lambda x: x.pos.y)
        
        for sprite in sprites_list:
            # Draw Connection Line (Magic Tether)
            # Only draw for summoned units
            if sprite in self.units:
                p_rect = self.camera.apply(self.player)
                s_rect = self.camera.apply(sprite)
                
                start = (p_rect.centerx, p_rect.centery)
                end = (s_rect.centerx, s_rect.centery)
                
                # Pulsing opacity for magic line
                alpha = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 150 + 50
                line_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(line_surf, (212, 175, 55, int(alpha)), start, end, 1)
                self.screen.blit(line_surf, (0,0))
            
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
        # Draw Particles (Front)
        self.particles.draw(self.screen, cam_offset)
        
        # Draw Attack Ranges (Visual Debug)
        # self.player.draw_attack_range(self.screen, cam_offset) # Removed
        for enemy in self.enemies:
            enemy.draw_attack_range(self.screen, cam_offset)
        
        # Draw HP bars for enemies
        for enemy in self.enemies:
            enemy.draw_hp_bar(self.screen, cam_offset)
            
        # HUD
        soul_text = self.font.render(f"Soul: {int(self.player.soul)}/{self.player.max_soul}", True, (200, 200, 255))
        self.screen.blit(soul_text, (20, 20))
        
        gold_text = self.font.render(f"Gold: {self.gold}/{self.target_gold}", True, (255, 215, 0))
        self.screen.blit(gold_text, (150, 20))
        
        # Player HP bar
        hp_text = self.font.render(f"HP: {self.player.hp}/{self.player.max_hp}", True, (255, 100, 100))
        self.screen.blit(hp_text, (20, 45))
        
        # Draw UI
        self.ui.draw(self.screen)
        self.ui.draw_unit_portraits(self.screen)
        
        # Player HP bar (visual)
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 70
        
        # Background
        pygame.draw.rect(self.screen, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        hp_ratio = self.player.hp / self.player.max_hp
        pygame.draw.rect(self.screen, (200, 0, 0), (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))
        
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Controls hint
        controls = self.font.render("WASD: Move | Space: Jump | X: Attack | 1: Summon", True, (150, 150, 150))
        self.screen.blit(controls, (20, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Show main menu
    next_state = show_main_menu(screen)
    
    if next_state == "game":
        # Start game
        g = Game()
        g.run()
    elif next_state == "story":
        # TODO: Show story screen
        print("Story screen not implemented yet")
    
    pygame.quit()
    sys.exit()
