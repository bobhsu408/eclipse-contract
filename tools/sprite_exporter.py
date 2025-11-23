#!/usr/bin/env python3
"""
sprite_exporter.py
將程式碼繪製的角色導出成 PNG 圖片
"""
import pygame
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def export_player_sprite():
    """導出玩家（召喚師）的圖片"""
    # 創建 Surface
    size = (50, 70)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # 透明背景
    
    # Colors
    ROBE_COLOR = (75, 0, 130)  # Indigo
    HOOD_COLOR = (48, 25, 52)  # Dark Purple
    SKIN_COLOR = (20, 20, 20)  # Shadowy
    EYE_COLOR = (0, 255, 255)  # Cyan Glow
    
    # Draw Robe
    pygame.draw.polygon(surface, ROBE_COLOR, [(10, 70), (40, 70), (35, 20), (15, 20)])
    
    # Hood/Head
    pygame.draw.circle(surface, HOOD_COLOR, (25, 20), 15)
    
    # Face
    pygame.draw.circle(surface, SKIN_COLOR, (25, 22), 8)
    
    # Eyes (facing right)
    pygame.draw.circle(surface, EYE_COLOR, (28, 22), 2)
    pygame.draw.circle(surface, EYE_COLOR, (22, 22), 2)
    
    # Staff (right side)
    pygame.draw.line(surface, (139, 69, 19), (45, 70), (45, 10), 3)  # Wood
    pygame.draw.circle(surface, (148, 0, 211), (45, 10), 5)  # Gem
    
    # Add glow effect around staff gem
    glow_surface = pygame.Surface(size, pygame.SRCALPHA)
    for i in range(3):
        alpha = 30 - i * 10
        radius = 8 + i * 2
        pygame.draw.circle(glow_surface, (148, 0, 211, alpha), (45, 10), radius)
    surface.blit(glow_surface, (0, 0))
    
    return surface

def export_ghoul_sprite():
    """導出食屍鬼的圖片"""
    # 創建 Surface
    size = (40, 40)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # 透明背景
    
    BODY_COLOR = (85, 107, 47)  # Olive Drab
    DARK_COLOR = (40, 50, 20)
    EYE_COLOR = (255, 50, 50)  # Red
    
    # Hunched Body
    pygame.draw.ellipse(surface, BODY_COLOR, (5, 10, 30, 25))
    
    # Head (facing right)
    pygame.draw.circle(surface, BODY_COLOR, (30, 15), 10)
    
    # Eye
    pygame.draw.circle(surface, EYE_COLOR, (33, 13), 2)
    
    # Arms/Claws
    pygame.draw.line(surface, DARK_COLOR, (20, 20), (35, 25), 3)
    
    # Add some texture/details
    # Spine bumps
    for i in range(3):
        x = 15 + i * 5
        y = 15 + i * 2
        pygame.draw.circle(surface, DARK_COLOR, (x, y), 2)
    
    return surface

def main():
    pygame.init()
    
    # 確保 assets 目錄存在
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    print("🎨 開始導出角色圖片...")
    
    # 導出玩家
    player_surface = export_player_sprite()
    player_path = os.path.join(assets_dir, 'player.png')
    pygame.image.save(player_surface, player_path)
    print(f"✅ 玩家圖片已保存: {player_path}")
    
    # 導出食屍鬼
    ghoul_surface = export_ghoul_sprite()
    ghoul_path = os.path.join(assets_dir, 'ghoul.png')
    pygame.image.save(ghoul_surface, ghoul_path)
    print(f"✅ 食屍鬼圖片已保存: {ghoul_path}")
    
    print("\n🎉 完成！現在遊戲會自動使用這些圖片。")
    print("💡 提示：你可以用任何繪圖軟體編輯這些 PNG 檔案來自訂角色外觀。")
    
    pygame.quit()

if __name__ == "__main__":
    main()
