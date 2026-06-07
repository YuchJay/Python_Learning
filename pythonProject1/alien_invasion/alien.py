"""外星人类 —— 支持普通、精英和Boss三种外星人变体。"""
import math
import os
import random

import pygame
from pygame.sprite import Sprite


class Alien(Sprite):  # 外星人（普通 / 精英 / Boss）
    # 类级别图像缓存
    _image_cache = None
    _elite_image_cache = None
    _boss_image_cache = None

    # 外星人类别常量
    TYPE_NORMAL = 'normal'
    TYPE_ELITE = 'elite'
    TYPE_BOSS = 'boss'

    @classmethod
    def _load_base_image(cls):
        """加载基础外星人图像（首次调用时从磁盘读取）。"""
        if cls._image_cache is None:
            image_path = os.path.join(os.path.dirname(__file__), 'images', 'alien.png')
            cls._image_cache = pygame.image.load(image_path)

    @classmethod
    def _get_image(cls, alien_type):
        """根据类型返回相应的缓存图像（用色调区分）。"""
        cls._load_base_image()
        if alien_type == cls.TYPE_BOSS:
            if cls._boss_image_cache is None:
                base = cls._image_cache
                w, h = base.get_size()
                scaled = pygame.transform.scale(
                    base, (int(w * 1.8), int(h * 1.8)))
                # 金色调
                tinted = scaled.copy()
                tinted.fill((255, 200, 50, 128), special_flags=pygame.BLEND_RGBA_ADD)
                cls._boss_image_cache = tinted
            return cls._boss_image_cache
        elif alien_type == cls.TYPE_ELITE:
            if cls._elite_image_cache is None:
                base = cls._image_cache
                # 品红色调
                tinted = base.copy()
                tint_surf = pygame.Surface(base.get_size(), pygame.SRCALPHA)
                tint_surf.fill((255, 60, 60, 100))
                base_copy = base.copy()
                base_copy.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                cls._elite_image_cache = base_copy
            return cls._elite_image_cache
        else:
            return cls._image_cache

    def __init__(self, ai_game, alien_type=None):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.ai_game = ai_game  # 保留引用以访问 sound_manager

        # 确定外星人类别
        if alien_type is not None:
            self.alien_type = alien_type
        else:
            self.alien_type = self._roll_type()

        self.image = Alien._get_image(self.alien_type)
        self.rect = self.image.get_rect()

        # 初始位置（屏幕左上角附近）
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        # 精确水平位置
        self.x = float(self.rect.x)

        # ── 属性差异化 ────────────────────────────────
        if self.alien_type == self.TYPE_ELITE:
            self.points = int(self.settings.alien_points
                              * self.settings.elite_points_multiplier)
            self.speed_multiplier = self.settings.elite_speed_multiplier
            self.health = 1
        elif self.alien_type == self.TYPE_BOSS:
            self.points = int(self.settings.alien_points
                              * self.settings.boss_points_multiplier)
            self.speed_multiplier = 0.7  # Boss移动更慢
            self.health = self.settings.boss_health
        else:
            self.points = self.settings.alien_points
            self.speed_multiplier = 1.0
            self.health = 1

        self.max_health = self.health

    def _roll_type(self):
        """根据当前游戏进度随机决定外星人类别。"""
        level = self.ai_game.stats.level if hasattr(self, 'ai_game') else 1
        # 精英概率随等级增长
        elite_chance = min(
            self.settings.elite_alien_max_chance,
            self.settings.elite_alien_chance_per_level * (level - 1))
        if random.random() < elite_chance:
            return self.TYPE_ELITE
        return self.TYPE_NORMAL

    def take_damage(self):
        """受到一次伤害，返回是否死亡。"""
        self.health -= 1
        # 受伤闪烁效果：短暂变白
        if self.health > 0:
            white = self.image.copy()
            white.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            self._flash_image = white
            self._flash_timer = 4  # 闪烁4帧
        return self.health <= 0

    @property
    def is_dead(self):
        return self.health <= 0

    def check_edges(self):  # 如果外星人位于屏幕边缘，返回True
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """移动外星人（考虑类别速度倍率和残血加速）。"""
        # 基础速度
        base_speed = self.settings.alien_speed * self.speed_multiplier

        # 残血加速（剩余敌人越少越快）
        if self.settings.fleet_ramp_enabled and hasattr(self, 'ai_game'):
            total_aliens = len(self.ai_game.aliens)
            if total_aliens > 0:
                # 初始外星人数量的近似值
                initial = 20  # 保守估计
                ratio = 1.0 - min(1.0, total_aliens / max(initial, total_aliens))
                ramp = 1.0 + ratio * (self.settings.fleet_ramp_max_multiplier - 1.0)
                base_speed *= ramp

        self.x += base_speed * self.settings.fleet_direction
        self.rect.x = int(self.x)

        # Boss受伤闪烁计时器
        if hasattr(self, '_flash_timer') and self._flash_timer > 0:
            self._flash_timer -= 1
