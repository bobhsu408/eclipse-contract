# main.py
import pygame
import sys
import math
from settings import *
from physics import Physics
from sprites import Player, Ghoul
from camera import Camera
from particles import ParticleSystem
from menu import show_main_menu

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
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        
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
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                
                if event.key == pygame.K_1:
                    if self.player.soul >= 10:
                        self.player.soul -= 10
                        spawn_x = self.player.pos.x + (50 if self.player.facing_right else -50)
                        spawn_y = self.player.pos.y
                        
                        ghoul = Ghoul(spawn_x, spawn_y)
                        self.units.add(ghoul)
                        self.all_sprites.add(ghoul)
                        
                        # Effect
                        self.particles.emit_summon_effect(spawn_x, spawn_y)
                        print("Summoned Ghoul")
                        
    def update(self):
        self.player.update(self.physics)
        
        # 未來可以加入敵人列表
        enemies = []  # TODO: 當有敵人系統時填入
        
        for unit in self.units:
            unit.update(self.physics, self.player, enemies)
        
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
            if sprite != self.player:
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
            
        # HUD
        soul_text = self.font.render(f"Soul: {int(self.player.soul)}", True, (200, 200, 255))
        self.screen.blit(soul_text, (20, 20))
        
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
