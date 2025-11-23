# menu.py
"""
主選單系統
包含：標題畫面、開始遊戲、設定、退出
"""
import pygame
import sys
from settings import *

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = (40, 20, 60)  # 深紫色
        self.hover_color = (80, 40, 120)  # 亮紫色
        self.border_color = (150, 100, 200)
        
    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        
        # 背景
        color = self.hover_color if is_hover else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # 文字
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 24)
        self.font_button = pygame.font.SysFont("Arial", 32)
        
        # 背景動畫
        self.bg_offset = 0
        self.particle_timer = 0
        self.particles = []
        
        # 按鈕
        center_x = SCREEN_WIDTH // 2
        start_y = 350
        button_width = 300
        button_height = 60
        spacing = 80
        
        self.buttons = [
            Button(center_x - button_width//2, start_y, button_width, button_height, 
                   "Start Game", self.start_game),
            Button(center_x - button_width//2, start_y + spacing, button_width, button_height,
                   "Story", self.show_story),
            Button(center_x - button_width//2, start_y + spacing*2, button_width, button_height,
                   "Settings", self.show_settings),
            Button(center_x - button_width//2, start_y + spacing*3, button_width, button_height,
                   "Quit", self.quit_game),
        ]
        
        self.running = True
        self.next_state = None
        
    def start_game(self):
        print("Starting game...")
        self.next_state = "game"
        self.running = False
        
    def show_story(self):
        print("Showing story...")
        self.next_state = "story"
        self.running = False
        
    def show_settings(self):
        print("Opening settings...")
        # TODO: 實作設定選單
        
    def quit_game(self):
        pygame.quit()
        sys.exit()
    
    def create_particle(self):
        """創建背景魔法粒子"""
        import random
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(-1, -0.3)
        color = random.choice([
            (148, 0, 211),   # 深紫
            (138, 43, 226),  # 藍紫
            (75, 0, 130),    # 靛藍
        ])
        size = random.randint(2, 5)
        life = random.randint(60, 120)
        
        return {
            'x': x, 'y': y, 
            'vx': vx, 'vy': vy,
            'color': color,
            'size': size,
            'life': life,
            'max_life': life
        }
    
    def update(self):
        # 背景滾動
        self.bg_offset += 0.2
        if self.bg_offset > SCREEN_HEIGHT:
            self.bg_offset = 0
        
        # 粒子生成
        self.particle_timer += 1
        if self.particle_timer > 10:
            self.particles.append(self.create_particle())
            self.particle_timer = 0
        
        # 粒子更新
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            
            if p['life'] <= 0 or p['y'] < -10:
                self.particles.remove(p)
    
    def draw(self):
        # 背景漸層
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(10 + ratio * 20)
            g = int(5 + ratio * 10)
            b = int(20 + ratio * 40)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # 背景網格（營造魔法陣感）
        grid_color = (40, 20, 60, 50)
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(int(self.bg_offset), SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y), 1)
        
        # 粒子
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            color = (*p['color'], alpha)
            s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (p['size'], p['size']), p['size'])
            self.screen.blit(s, (p['x'] - p['size'], p['y'] - p['size']))
        
        # 標題
        title = self.font_title.render("Eclipse Contract", True, (200, 150, 255))
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 150))
        
        # 標題陰影
        shadow = self.font_title.render("Eclipse Contract", True, (50, 20, 80))
        shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH//2 + 3, 153))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(title, title_rect)
        
        # 副標題
        subtitle = self.font_subtitle.render("The Necromancer's Debt", True, (180, 180, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 按鈕
        for button in self.buttons:
            button.draw(self.screen, self.font_button)
        
        # 版本號
        version = pygame.font.SysFont("Arial", 14).render("Alpha 0.2", True, (100, 100, 120))
        self.screen.blit(version, (10, SCREEN_HEIGHT - 25))
    
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                self.handle_event(event)
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            clock.tick(60)
        
        return self.next_state

def show_main_menu(screen):
    """顯示主選單並返回下一個狀態"""
    menu = MainMenu(screen)
    return menu.run()
