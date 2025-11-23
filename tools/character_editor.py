# tools/character_editor.py
import pygame
import sys
import os
import json
import subprocess

# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import *

AI_TYPES = ["follow", "guard", "patrol", "aggressive", "flee", "wander"]

AI_DESCRIPTIONS = {
    "follow": "Follow Player",
    "guard": "Guard Position",
    "patrol": "Patrol Area",
    "aggressive": "Attack Enemies",
    "flee": "Flee from Danger",
    "wander": "Wander Around"
}

def open_file_dialog(initial_dir):
    """Open file dialog using AppleScript (macOS)"""
    script = f'''
    tell application "System Events"
        activate
        set theFile to choose file with prompt "Select Character Image" of type {{"PNG", "public.png"}} default location POSIX file "{initial_dir}"
        return POSIX path of theFile
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def save_file_dialog(initial_dir, default_name):
    """Open save dialog using AppleScript (macOS)"""
    script = f'''
    tell application "System Events"
        activate
        set theFile to choose file name with prompt "Save Character Config" default name "{default_name}" default location POSIX file "{initial_dir}"
        return POSIX path of theFile
    end tell
    '''
    try:
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            path = result.stdout.strip()
            if not path.endswith('.json'):
                path += '.json'
            return path
    except:
        pass
    return None

class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = (50, 50, 50)
        self.hover_color = (70, 70, 70)
        
    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False

class TextInput:
    def __init__(self, x, y, w, h, initial_text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = initial_text
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def draw(self, surface, font):
        # Background
        color = (60, 60, 60) if self.active else (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        border_color = (100, 150, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        # Text
        display_text = self.text
        if self.active and self.cursor_visible:
            display_text += "|"
        
        text_surf = font.render(display_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Blink cursor
        self.cursor_timer += 1
        if self.cursor_timer > 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
            
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                self.active = False
                return True
            elif event.unicode.isprintable() and len(self.text) < 20:
                self.text += event.unicode
                return True
        
        return False


class Dropdown:
    def __init__(self, x, y, w, h, options, current_value, on_select, descriptions):
        self.rect = pygame.Rect(x, y, w, h)
        self.options = options
        self.current_value = current_value
        self.on_select = on_select
        self.descriptions = descriptions
        self.is_open = False
        
        # Search functionality
        self.search_text = ""
        self.filtered_options = options.copy()
        
        # Scroll functionality
        self.scroll_offset = 0
        self.max_visible_items = 5
        self.item_height = 40
        
    def filter_options(self):
        """Filter options based on search text"""
        if not self.search_text:
            self.filtered_options = self.options.copy()
        else:
            self.filtered_options = [
                opt for opt in self.options 
                if self.search_text.lower() in opt.lower() or 
                   self.search_text.lower() in self.descriptions.get(opt, "").lower()
            ]
        self.scroll_offset = 0  # Reset scroll when filtering
        
    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        
        # Main button
        color = (60, 60, 60) if self.rect.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1)
        
        # Current value
        display_text = self.descriptions.get(self.current_value, self.current_value)
        text_surf = font.render(display_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Arrow
        arrow = "v" if not self.is_open else "^"
        arrow_surf = font.render(arrow, True, (200, 200, 200))
        arrow_rect = arrow_surf.get_rect(midright=(self.rect.right - 10, self.rect.centery))
        surface.blit(arrow_surf, arrow_rect)
        
        # Dropdown list
        if self.is_open:
            # Search box
            search_box_height = 35
            search_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, search_box_height)
            pygame.draw.rect(surface, (35, 35, 35), search_rect)
            pygame.draw.rect(surface, (100, 100, 100), search_rect, 1)
            
            # Search text
            search_display = f"Search: {self.search_text}_" if self.search_text or search_rect.collidepoint(mouse_pos) else "Type to search..."
            search_surf = font.render(search_display, True, (180, 180, 180))
            search_text_rect = search_surf.get_rect(midleft=(search_rect.x + 10, search_rect.centery))
            surface.blit(search_surf, search_text_rect)
            
            # Options list
            visible_items = min(self.max_visible_items, len(self.filtered_options))
            list_height = visible_items * self.item_height
            list_rect = pygame.Rect(self.rect.x, search_rect.bottom, self.rect.width, list_height)
            
            pygame.draw.rect(surface, (40, 40, 40), list_rect)
            pygame.draw.rect(surface, (200, 200, 200), list_rect, 1)
            
            # Draw visible options
            start_idx = self.scroll_offset
            end_idx = min(start_idx + visible_items, len(self.filtered_options))
            
            for i in range(start_idx, end_idx):
                option = self.filtered_options[i]
                local_idx = i - start_idx
                option_rect = pygame.Rect(
                    self.rect.x, 
                    search_rect.bottom + local_idx * self.item_height, 
                    self.rect.width, 
                    self.item_height
                )
                
                if option_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(surface, (70, 70, 70), option_rect)
                
                if option == self.current_value:
                    pygame.draw.rect(surface, (100, 50, 150), option_rect.inflate(-4, -4))
                
                display = self.descriptions.get(option, option)
                opt_surf = font.render(display, True, (255, 255, 255))
                opt_rect = opt_surf.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
                surface.blit(opt_surf, opt_rect)
            
            # Scroll indicator
            if len(self.filtered_options) > self.max_visible_items:
                indicator_text = f"{start_idx + 1}-{end_idx} of {len(self.filtered_options)}"
                indicator_surf = pygame.font.SysFont("Arial", 12).render(indicator_text, True, (150, 150, 150))
                surface.blit(indicator_surf, (self.rect.x + 5, list_rect.bottom + 2))
    
    def handle_event(self, event):
        if not self.is_open:
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                self.is_open = True
                self.search_text = ""
                self.filter_options()
                return True
            return False
        
        # When open, handle events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.search_text = self.search_text[:-1]
                self.filter_options()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.is_open = False
                self.search_text = ""
                return True
            elif event.key == pygame.K_RETURN and self.filtered_options:
                # Select first filtered option
                self.current_value = self.filtered_options[self.scroll_offset]
                self.on_select(self.current_value)
                self.is_open = False
                self.search_text = ""
                return True
            elif event.unicode.isprintable():
                self.search_text += event.unicode
                self.filter_options()
                return True
                
        elif event.type == pygame.MOUSEWHEEL:
            # Scroll through options
            self.scroll_offset = max(0, min(
                len(self.filtered_options) - self.max_visible_items,
                self.scroll_offset - event.y
            ))
            return True
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if clicked on search box
            search_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, 35)
            if search_rect.collidepoint(event.pos):
                return True  # Just keep focus
            
            # Check if clicked on an option
            list_start_y = search_rect.bottom
            visible_items = min(self.max_visible_items, len(self.filtered_options))
            
            for i in range(self.scroll_offset, min(self.scroll_offset + visible_items, len(self.filtered_options))):
                local_idx = i - self.scroll_offset
                option_rect = pygame.Rect(
                    self.rect.x, 
                    list_start_y + local_idx * self.item_height, 
                    self.rect.width, 
                    self.item_height
                )
                if option_rect.collidepoint(event.pos):
                    self.current_value = self.filtered_options[i]
                    self.on_select(self.current_value)
                    self.is_open = False
                    self.search_text = ""
                    return True
            
            # Clicked outside - close
            self.is_open = False
            self.search_text = ""
            
        return False


class Editor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("Eclipse Contract - Character Editor")
        self.clock = pygame.time.Clock()
        
        # Fonts - larger and clearer
        self.font = pygame.font.SysFont("Arial", 18)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # State
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.char_data = {
            "name": "NewUnit",
            "image": None,
            "scale": 1.0,
            "speed": 2.0,
            "hp": 100,
            "ai_type": "follow",
            "ai_params": {
                "follow_distance": 80,
                "stop_distance": 50
            }
        }
        
        self.preview_pos = [600, 350]
        self.loaded_image = None
        
        # Name input
        self.name_input = TextInput(20, 520, 180, 35, self.char_data["name"])
        
        # UI - Left Panel
        y_offset = 70
        self.buttons = [
            Button(20, y_offset, 180, 35, "Select Image", self.select_image),
        ]
        y_offset += 50
        
        self.buttons.extend([
            Button(20, y_offset, 180, 35, "Scale +", lambda: self.adjust_scale(0.1)),
            Button(20, y_offset + 40, 180, 35, "Scale -", lambda: self.adjust_scale(-0.1)),
        ])
        y_offset += 90
        
        self.buttons.extend([
            Button(20, y_offset, 180, 35, "Speed +", lambda: self.adjust_speed(0.5)),
            Button(20, y_offset + 40, 180, 35, "Speed -", lambda: self.adjust_speed(-0.5)),
        ])
        y_offset += 90
        
        self.buttons.extend([
            Button(20, y_offset, 180, 35, "HP +10", lambda: self.adjust_hp(10)),
            Button(20, y_offset + 40, 180, 35, "HP -10", lambda: self.adjust_hp(-10)),
        ])
        y_offset += 90
        
        # AI Dropdown
        self.ai_dropdown = Dropdown(20, y_offset, 180, 35, AI_TYPES, 
                                    self.char_data["ai_type"], self.on_ai_select, AI_DESCRIPTIONS)
        y_offset += 50
        
        # Save
        self.buttons.append(
            Button(20, 630, 180, 45, "SAVE JSON", self.save_json)
        )
        
    def select_image(self):
        """Open system file dialog"""
        print("Opening file dialog...")
        file_path = open_file_dialog(self.assets_dir)
        
        if file_path:
            print(f"Selected: {file_path}")
            self.char_data["image"] = os.path.basename(file_path)
            
            # Copy to assets if not already there
            if not file_path.startswith(self.assets_dir):
                import shutil
                dest = os.path.join(self.assets_dir, self.char_data["image"])
                shutil.copy(file_path, dest)
                print(f"Copied to: {dest}")
            
            self.load_current_image()
        else:
            print("No file selected")
        
    def load_current_image(self):
        if not self.char_data["image"]: return
        path = os.path.join(self.assets_dir, self.char_data["image"])
        try:
            img = pygame.image.load(path).convert_alpha()
            w = int(img.get_width() * self.char_data["scale"])
            h = int(img.get_height() * self.char_data["scale"])
            self.loaded_image = pygame.transform.scale(img, (w, h))
        except Exception as e:
            print(f"Failed to load image: {e}")
            self.loaded_image = None
        
    def adjust_scale(self, amount):
        self.char_data["scale"] = max(0.1, min(5.0, self.char_data["scale"] + amount))
        self.load_current_image()
        
    def adjust_speed(self, amount):
        self.char_data["speed"] = max(0.5, self.char_data["speed"] + amount)
        
    def adjust_hp(self, amount):
        self.char_data["hp"] = max(10, self.char_data["hp"] + amount)
        
    def on_ai_select(self, ai_type):
        self.char_data["ai_type"] = ai_type
        
        # Set default parameters
        if ai_type == "follow":
            self.char_data["ai_params"] = {"follow_distance": 80, "stop_distance": 50}
        elif ai_type == "guard":
            self.char_data["ai_params"] = {"guard_radius": 100}
        elif ai_type == "patrol":
            self.char_data["ai_params"] = {"patrol_distance": 200}
        elif ai_type == "aggressive":
            self.char_data["ai_params"] = {"attack_range": 150, "chase_range": 300}
        elif ai_type == "flee":
            self.char_data["ai_params"] = {"flee_distance": 200}
        elif ai_type == "wander":
            self.char_data["ai_params"] = {"wander_radius": 150}

    def save_json(self):
        if not self.char_data["image"]:
            print("Please select an image first!")
            return
        
        default_name = self.char_data["image"].replace('.png', '.json')
        
        print("Opening save dialog...")
        file_path = save_file_dialog(self.data_dir, default_name)
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.char_data, f, indent=4, ensure_ascii=False)
            print(f"Saved to: {file_path}")
        else:
            print("Save cancelled")

    def run(self):
        while True:
            self.screen.fill((30, 30, 30))
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle text input first
                if self.name_input.handle_event(event):
                    self.char_data["name"] = self.name_input.text
                    continue
                
                if self.ai_dropdown.handle_event(event):
                    continue
                    
                for btn in self.buttons:
                    if btn.handle_event(event):
                        break
            
            # Preview Area
            pygame.draw.rect(self.screen, (40, 40, 40), (220, 0, 780, 700))
            pygame.draw.line(self.screen, (60, 60, 60), (220, 350), (1000, 350))
            pygame.draw.line(self.screen, (60, 60, 60), (610, 0), (610, 700))
            
            # Preview
            if self.loaded_image:
                rect = self.loaded_image.get_rect(center=self.preview_pos)
                pygame.draw.ellipse(self.screen, (0,0,0,100), 
                                  (rect.centerx - rect.width/2, rect.bottom - 5, rect.width, 10))
                self.screen.blit(self.loaded_image, rect)
            else:
                no_img_text = self.font.render("Click 'Select Image' to start", True, (150, 150, 150))
                self.screen.blit(no_img_text, (480, 340))
            
            # UI Panel
            pygame.draw.rect(self.screen, (25, 25, 25), (0, 0, 220, 700))
            
            title = self.title_font.render("Character Editor", True, (200, 200, 255))
            self.screen.blit(title, (25, 20))
            
            # Name label
            name_label = self.font.render("Name:", True, (180, 180, 180))
            self.screen.blit(name_label, (20, 495))
            
            # Draw UI elements
            self.name_input.draw(self.screen, self.font)
            
            for btn in self.buttons:
                btn.draw(self.screen, self.font)
            
            self.ai_dropdown.draw(self.screen, self.font)
                
            # Info Panel
            info = [
                f"Image: {self.char_data['image'] or 'None'}",
                f"Scale: {self.char_data['scale']:.1f}x",
                f"Speed: {self.char_data['speed']:.1f}",
                f"HP: {self.char_data['hp']}",
                "",
                f"AI Type: {AI_DESCRIPTIONS[self.char_data['ai_type']]}",
                "AI Parameters:",
            ]
            
            for key, val in self.char_data["ai_params"].items():
                info.append(f"  {key}: {val}")
            
            y = 60
            for line in info:
                color = (255, 200, 100) if "AI" in line or "Parameters" in line else (220, 220, 220)
                surf = self.font.render(line, True, color)
                self.screen.blit(surf, (240, y))
                y += 30
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    Editor().run()
