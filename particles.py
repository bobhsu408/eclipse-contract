# particles.py
import pygame
import random

class Particle:
    def __init__(self, x, y, color, velocity, life):
        self.x = x
        self.y = y
        self.color = color
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface, camera_offset):
        if self.life > 0:
            # Fade out alpha
            alpha = int((self.life / self.max_life) * 255)
            s = pygame.Surface((int(self.size)*2, int(self.size)*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
            
            pos = (int(self.x) + camera_offset[0], int(self.y) + camera_offset[1])
            surface.blit(s, pos)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, color, velocity, life):
        self.particles.append(Particle(x, y, color, velocity, life))

    def emit_summon_effect(self, x, y):
        # Burst of purple/cyan particles
        for _ in range(20):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            color = random.choice([(148, 0, 211), (0, 255, 255), (75, 0, 130)])
            self.add_particle(x, y, color, (vx, vy), random.randint(20, 40))

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw(self, surface, camera_offset):
        for p in self.particles:
            p.draw(surface, camera_offset)

import math
