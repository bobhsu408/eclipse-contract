# ai.py
"""
所有單位的 AI 邏輯集中管理
每個 AI 行為都是一個獨立的類別
"""
import pygame
import random
import math

class AIBehavior:
    """AI 行為基礎類別"""
    def __init__(self, entity):
        self.entity = entity
        
    def update(self, physics, player, enemies=None):
        """更新 AI 行為 - 子類別需要實作這個方法"""
        pass

class FollowPlayerAI(AIBehavior):
    """跟隨玩家的 AI"""
    def __init__(self, entity, follow_distance=80, stop_distance=50):
        super().__init__(entity)
        self.follow_distance = follow_distance
        self.stop_distance = stop_distance
        
    def update(self, physics, player, enemies=None):
        diff = player.pos - self.entity.pos
        dist = diff.length()
        
        if dist > self.follow_distance:
            # 距離太遠，追上去
            diff.normalize_ip()
            self.entity.vel += diff * self.entity.speed
            
            # 面向玩家
            if diff.x > 0: 
                self.entity.facing_right = True
            else: 
                self.entity.facing_right = False
        elif dist < self.stop_distance:
            # 太近了，稍微後退
            diff.normalize_ip()
            self.entity.vel -= diff * (self.entity.speed * 0.3)
        else:
            # 在理想距離，減速
            self.entity.vel *= 0.9

class GuardPositionAI(AIBehavior):
    """守衛固定位置的 AI"""
    def __init__(self, entity, guard_radius=100):
        super().__init__(entity)
        self.guard_pos = entity.pos.copy()  # 記住初始位置
        self.guard_radius = guard_radius
        
    def update(self, physics, player, enemies=None):
        # 計算離守衛點的距離
        diff = self.guard_pos - self.entity.pos
        dist = diff.length()
        
        if dist > 10:  # 如果離守衛點太遠
            diff.normalize_ip()
            self.entity.vel += diff * self.entity.speed * 0.5
        else:
            # 已經在守衛點附近，減速
            self.entity.vel *= 0.8

class PatrolAI(AIBehavior):
    """巡邏 AI - 在兩點之間來回"""
    def __init__(self, entity, patrol_distance=200):
        super().__init__(entity)
        self.start_pos = entity.pos.copy()
        self.patrol_distance = patrol_distance
        self.target_offset = patrol_distance
        self.wait_timer = 0
        self.wait_duration = 60  # 到達目標後等待的幀數
        
    def update(self, physics, player, enemies=None):
        if self.wait_timer > 0:
            self.wait_timer -= 1
            self.entity.vel *= 0.9
            return
            
        target = self.start_pos + pygame.math.Vector2(self.target_offset, 0)
        diff = target - self.entity.pos
        dist = diff.length()
        
        if dist < 20:  # 到達目標點
            self.target_offset *= -1  # 反轉方向
            self.wait_timer = self.wait_duration
            self.entity.facing_right = self.target_offset > 0
        else:
            diff.normalize_ip()
            self.entity.vel += diff * self.entity.speed * 0.5
            self.entity.facing_right = diff.x > 0

class AggressiveAI(AIBehavior):
    """攻擊性 AI - 主動攻擊最近的敵人"""
    def __init__(self, entity, attack_range=150, chase_range=300):
        super().__init__(entity)
        self.attack_range = attack_range
        self.chase_range = chase_range
        
    def update(self, physics, player, enemies=None):
        if not enemies:
            # 沒有敵人，跟隨玩家
            diff = player.pos - self.entity.pos
            dist = diff.length()
            if dist > 100:
                diff.normalize_ip()
                self.entity.vel += diff * self.entity.speed * 0.5
            return
            
        # 找最近的敵人
        closest_enemy = None
        min_dist = float('inf')
        
        for enemy in enemies:
            dist = (enemy.pos - self.entity.pos).length()
            if dist < min_dist:
                min_dist = dist
                closest_enemy = enemy
                
        if closest_enemy and min_dist < self.chase_range:
            diff = closest_enemy.pos - self.entity.pos
            diff.normalize_ip()
            
            if min_dist > self.attack_range:
                # 追擊
                self.entity.vel += diff * self.entity.speed
            else:
                # 在攻擊範圍內，稍微保持距離
                self.entity.vel += diff * self.entity.speed * 0.3
                
            self.entity.facing_right = diff.x > 0

class FleeAI(AIBehavior):
    """逃跑 AI - 遠離危險"""
    def __init__(self, entity, flee_distance=200):
        super().__init__(entity)
        self.flee_distance = flee_distance
        
    def update(self, physics, player, enemies=None):
        if not enemies:
            return
            
        # 計算所有敵人的平均位置
        danger_center = pygame.math.Vector2(0, 0)
        for enemy in enemies:
            danger_center += enemy.pos
        danger_center /= len(enemies)
        
        # 遠離危險中心
        diff = self.entity.pos - danger_center
        dist = diff.length()
        
        if dist < self.flee_distance:
            diff.normalize_ip()
            self.entity.vel += diff * self.entity.speed * 1.5  # 逃跑速度加成
            self.entity.facing_right = diff.x > 0

class WanderAI(AIBehavior):
    """隨機遊蕩 AI"""
    def __init__(self, entity, wander_radius=150):
        super().__init__(entity)
        self.home_pos = entity.pos.copy()
        self.wander_radius = wander_radius
        self.target = self.get_random_target()
        self.wait_timer = 0
        
    def get_random_target(self):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(50, self.wander_radius)
        offset = pygame.math.Vector2(math.cos(angle) * dist, math.sin(angle) * dist)
        return self.home_pos + offset
        
    def update(self, physics, player, enemies=None):
        if self.wait_timer > 0:
            self.wait_timer -= 1
            self.entity.vel *= 0.95
            return
            
        diff = self.target - self.entity.pos
        dist = diff.length()
        
        if dist < 30:  # 到達目標
            self.target = self.get_random_target()
            self.wait_timer = random.randint(30, 120)
        else:
            diff.normalize_ip()
            self.entity.vel += diff * self.entity.speed * 0.3
            self.entity.facing_right = diff.x > 0

class CommandableAI(AIBehavior):
    """可指揮的 AI - 可以在不同模式間切換"""
    def __init__(self, entity):
        super().__init__(entity)
        self.mode = "follow" # default
        
        # Sub-behaviors
        self.follow_ai = FollowPlayerAI(entity, follow_distance=80)
        
        # Use entity stats if available
        attack_range = getattr(entity, 'attack_range', 40)
        self.attack_ai = AggressiveAI(entity, attack_range=attack_range, chase_range=400)
        
        self.guard_ai = GuardPositionAI(entity)
        
    def set_mode(self, mode):
        if mode in ["follow", "attack", "defend"]:
            self.mode = mode
            if mode == "defend":
                # Reset guard position to current position
                self.guard_ai.guard_pos = self.entity.pos.copy()
            
    def update(self, physics, player, enemies=None):
        if self.mode == "follow":
            self.follow_ai.update(physics, player, enemies)
        elif self.mode == "attack":
            self.attack_ai.update(physics, player, enemies)
        elif self.mode == "defend":
            self.guard_ai.update(physics, player, enemies)

# AI 類型對照表 - 方便從字串創建 AI
AI_TYPES = {
    "follow": FollowPlayerAI,
    "guard": GuardPositionAI,
    "patrol": PatrolAI,
    "aggressive": AggressiveAI,
    "flee": FleeAI,
    "wander": WanderAI,
    "commandable": CommandableAI,
}

def create_ai(ai_type, entity, **kwargs):
    """
    根據類型字串創建 AI
    
    參數:
        ai_type: AI 類型字串 (例如 "follow", "guard")
        entity: 要控制的實體
        **kwargs: AI 的額外參數
    """
    ai_class = AI_TYPES.get(ai_type, FollowPlayerAI)
    return ai_class(entity, **kwargs)
