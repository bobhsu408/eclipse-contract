# settings.py
import pygame

# Screen Settings
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "Eclipse Contract (Python)"

# World Settings
WORLD_WIDTH = 2000
WORLD_HEIGHT = 1500

# Colors
COLOR_BG = (10, 10, 12) # Dark
COLOR_PLAYER = (123, 44, 191) # Purple
COLOR_GOLD = (212, 175, 55)
COLOR_GHOUL = (85, 107, 47) # Olive Green
COLOR_GROUND = (26, 26, 26)
COLOR_GRID = (255, 255, 255, 10) # Alpha not supported directly in tuple for some draws, handled in logic

# Physics
GRAVITY = 0.9
FRICTION = 0.85
GROUND_HORIZON = 200 # Min Y
