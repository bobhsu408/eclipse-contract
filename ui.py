import pygame
from settings import *
from sprites import Ghoul, Wisp

class SummonUI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 16, bold=True)
        
        # Unit Types configuration
        self.unit_types = [
            {
                "name": "Ghoul",
                "class": Ghoul,
                "cost": 10,
                "key": pygame.K_1,
                "key_str": "1",
                "color": (85, 107, 47),
            },
            {
                "name": "Wisp",
                "class": Wisp,
                "cost": 15,
                "key": pygame.K_2,
                "key_str": "2",
                "color": (200, 255, 255),
            }
        ]
        
        # Layout
        self.slot_size = 60
        self.padding = 10
        self.start_x = (SCREEN_WIDTH - (len(self.unit_types) * (self.slot_size + self.padding))) // 2
        self.y = SCREEN_HEIGHT - 80
        
        # Context menu state
        self.selected_unit = None
        self.selected_unit_index = None
        self.show_menu = False
        self.menu_x = 0
        self.menu_y = 0
        
    def draw(self, surface):
        for i, unit in enumerate(self.unit_types):
            x = self.start_x + i * (self.slot_size + self.padding)
            
            # Slot Background
            rect = pygame.Rect(x, self.y, self.slot_size, self.slot_size)
            pygame.draw.rect(surface, (50, 50, 50), rect)
            
            # Highlight if affordable
            if self.game.player.soul >= unit["cost"]:
                pygame.draw.rect(surface, (255, 255, 255), rect, 2)
            else:
                pygame.draw.rect(surface, (100, 50, 50), rect, 2)
            
            # Unit Icon (Color)
            icon_rect = rect.inflate(-20, -20)
            pygame.draw.rect(surface, unit["color"], icon_rect)
            
            # Cost
            cost_surf = self.font.render(str(unit["cost"]), True, (255, 215, 0))
            surface.blit(cost_surf, (x + 5, self.y + 5))
            
            # Key
            key_surf = self.font.render(unit["key_str"], True, (255, 255, 255))
            surface.blit(key_surf, (x + 40, self.y + 40))
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = pygame.mouse.get_pos()
                
                # Check if clicking on context menu
                if self.show_menu:
                    if self.handle_menu_click(mx, my):
                        return True
                    else:
                        # Click outside menu, close it
                        self.show_menu = False
                        self.selected_unit = None
                        self.selected_unit_index = None
                        return True
                
                # Check portrait clicks
                if self.handle_portrait_click(mx, my):
                    return True
                
                # Check summon slot clicks
                for i, unit in enumerate(self.unit_types):
                    x = self.start_x + i * (self.slot_size + self.padding)
                    slot_rect = pygame.Rect(x, self.y, self.slot_size, self.slot_size)
                    if slot_rect.collidepoint(mx, my):
                        self.summon(unit)
                        return True
                        
        if event.type == pygame.KEYDOWN:
            for unit in self.unit_types:
                if event.key == unit["key"]:
                    self.summon(unit)
                    
    def handle_portrait_click(self, mx, my):
        """處理頭像點擊"""
        portrait_size = 50
        padding = 10
        start_y = 100
        
        units_list = list(self.game.units)
        for i, unit in enumerate(units_list):
            y = start_y + i * (portrait_size + padding)
            x = 10
            center = (x + portrait_size // 2, y + portrait_size // 2)
            
            # Check if click is within portrait circle
            dist = ((mx - center[0])**2 + (my - center[1])**2)**0.5
            if dist <= portrait_size // 2:
                self.selected_unit = unit
                self.selected_unit_index = i
                self.show_menu = True
                self.menu_x = x + portrait_size + 10
                self.menu_y = y
                return True
        return False
        
    def handle_menu_click(self, mx, my):
        """處理選單點擊"""
        if not self.show_menu or not self.selected_unit:
            return False
            
        menu_width = 120
        menu_height = 120
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, menu_width, menu_height)
        
        if not menu_rect.collidepoint(mx, my):
            return False
            
        # Mode buttons
        modes = ["follow", "attack", "defend"]
        button_height = 30
        
        for i, mode in enumerate(modes):
            button_y = self.menu_y + 10 + i * (button_height + 5)
            button_rect = pygame.Rect(self.menu_x + 10, button_y, menu_width - 20, button_height)
            
            if button_rect.collidepoint(mx, my):
                # Set mode for this specific unit
                if hasattr(self.selected_unit, 'ai') and hasattr(self.selected_unit.ai, 'set_mode'):
                    self.selected_unit.ai.set_mode(mode)
                    print(f"Set unit mode to {mode}")
                self.show_menu = False
                self.selected_unit = None
                self.selected_unit_index = None
                return True
                
        return True
                    
    def summon(self, unit_data):
        if self.game.player.soul >= unit_data["cost"]:
            self.game.player.soul -= unit_data["cost"]
            
            spawn_x = self.game.player.pos.x + (50 if self.game.player.facing_right else -50)
            spawn_y = self.game.player.pos.y
            
            new_unit = unit_data["class"](spawn_x, spawn_y)
            
            self.game.units.add(new_unit)
            self.game.all_sprites.add(new_unit)
            self.game.particles.emit_summon_effect(spawn_x, spawn_y)
            print(f"Summoned {unit_data['name']}")
                    
    def draw_unit_portraits(self, surface):
        """繪製左側單位頭像面板"""
        if not self.game.units:
            return
            
        portrait_size = 50
        padding = 10
        start_y = 100
        
        units_list = list(self.game.units)
        for i, unit in enumerate(units_list):
            y = start_y + i * (portrait_size + padding)
            x = 10
            
            # Highlight if selected
            if self.selected_unit == unit and self.show_menu:
                highlight_rect = pygame.Rect(x - 3, y - 3, portrait_size + 6, portrait_size + 6)
                pygame.draw.rect(surface, (255, 255, 100), highlight_rect, 3)
            
            # Background circle
            center = (x + portrait_size // 2, y + portrait_size // 2)
            pygame.draw.circle(surface, (40, 40, 40), center, portrait_size // 2)
            
            # Unit color (based on type)
            if hasattr(unit, 'image'):
                if isinstance(unit, Ghoul):
                    pygame.draw.circle(surface, (85, 107, 47), center, portrait_size // 2 - 5)
                elif isinstance(unit, Wisp):
                    pygame.draw.circle(surface, (200, 255, 255), center, portrait_size // 2 - 5)
            
            # HP bar (circular arc)
            if hasattr(unit, 'hp') and hasattr(unit, 'max_hp'):
                hp_percent = unit.hp / unit.max_hp
                
                # Determine color
                if hp_percent < 0.2:
                    bar_color = (255, 50, 50)  # Red
                else:
                    bar_color = (50, 255, 50)  # Green
                
                # Draw arc
                import math
                radius = portrait_size // 2 + 3
                thickness = 4
                
                # Calculate arc angle (0 = top, clockwise)
                start_angle = -math.pi / 2  # Start from top
                end_angle = start_angle + (2 * math.pi * hp_percent)
                
                # Draw arc using lines
                if hp_percent > 0:
                    points = []
                    num_points = max(int(hp_percent * 30), 2)
                    for j in range(num_points + 1):
                        angle = start_angle + (end_angle - start_angle) * (j / num_points)
                        px = center[0] + radius * math.cos(angle)
                        py = center[1] + radius * math.sin(angle)
                        points.append((px, py))
                    
                    if len(points) > 1:
                        pygame.draw.lines(surface, bar_color, False, points, thickness)
        
        # Draw context menu if active
        if self.show_menu and self.selected_unit:
            self.draw_context_menu(surface)
            
    def draw_context_menu(self, surface):
        """繪製右鍵選單"""
        menu_width = 120
        menu_height = 120
        
        # Menu background
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, menu_width, menu_height)
        pygame.draw.rect(surface, (30, 30, 30), menu_rect)
        pygame.draw.rect(surface, (200, 200, 200), menu_rect, 2)
        
        # Title
        title_surf = self.title_font.render("Mode", True, (255, 255, 255))
        surface.blit(title_surf, (self.menu_x + 10, self.menu_y + 5))
        
        # Mode buttons
        modes = [
            ("Follow", "follow", (50, 200, 50)),
            ("Attack", "attack", (200, 50, 50)),
            ("Defend", "defend", (50, 50, 200))
        ]
        
        button_height = 25
        current_mode = getattr(self.selected_unit.ai, 'mode', 'follow') if hasattr(self.selected_unit, 'ai') else 'follow'
        
        for i, (label, mode, color) in enumerate(modes):
            button_y = self.menu_y + 30 + i * (button_height + 5)
            button_rect = pygame.Rect(self.menu_x + 10, button_y, menu_width - 20, button_height)
            
            # Highlight current mode
            if mode == current_mode:
                pygame.draw.rect(surface, color, button_rect)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(surface, (60, 60, 60), button_rect)
                text_color = (200, 200, 200)
                
            pygame.draw.rect(surface, (150, 150, 150), button_rect, 1)
            
            text_surf = self.font.render(label, True, text_color)
            text_rect = text_surf.get_rect(center=button_rect.center)
            surface.blit(text_surf, text_rect)
