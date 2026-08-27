"""道具系统 —— 外星人被摧毁时概率掉落，飞船拾取后获得限时增益。"""
import math
import random
import pygame
from pygame.sprite import Sprite


class PowerUpType:
    """道具类型枚举"""
    RAPID_FIRE = 'rapid_fire'    # 🔥 双倍射速
    SHIELD = 'shield'            # 🛡 临时无敌
    SPREAD_SHOT = 'spread_shot'  # ⚡ 三向射击
    EXTRA_LIFE = 'extra_life'    # ❤ 额外生命

    # 掉落权重（数值越大越常见）
    WEIGHTS = {
        RAPID_FIRE: 30,
        SHIELD: 25,
        SPREAD_SHOT: 25,
        EXTRA_LIFE: 20,
    }

    # 视觉颜色
    COLORS = {
        RAPID_FIRE: (255, 80, 0),     # 橙红
        SHIELD: (0, 180, 255),        # 天蓝
        SPREAD_SHOT: (255, 220, 0),   # 金黄
        EXTRA_LIFE: (0, 255, 80),     # 翠绿
    }

    # 图标字符（用于简单渲染）
    SYMBOLS = {
        RAPID_FIRE: '⚡',
        SHIELD: '🛡',
        SPREAD_SHOT: '✦',
        EXTRA_LIFE: '♥',
    }


class PowerUp(Sprite):
    """可掉落的道具精灵 —— 从外星人被摧毁位置下落。"""

    def __init__(self, ai_game, x, y):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = self.screen.get_rect()

        # 按权重随机选择道具类型
        types = list(PowerUpType.WEIGHTS.keys())
        weights = list(PowerUpType.WEIGHTS.values())
        self.power_type = random.choices(types, weights=weights, k=1)[0]

        self.color = PowerUpType.COLORS[self.power_type]

        # 绘制道具外观（带光晕的圆点）
        size = 24
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        # 外发光
        pygame.draw.circle(self.image, (*self.color, 80), (size // 2, size // 2), size // 2)
        # 内核
        pygame.draw.circle(self.image, (*self.color, 220), (size // 2, size // 2), size // 3)
        # 白色高光
        pygame.draw.circle(self.image, (255, 255, 255, 180), (size // 2 - 2, size // 2 - 2), size // 6)

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

        self.y = float(self.rect.y)
        # 轻微的水平摆动
        self.wobble_phase = random.uniform(0, 6.28)

    def update(self):
        """下落（带轻微左右摆动，更自然）。"""
        self.y += self.settings.powerup_fall_speed
        self.wobble_phase += 0.05
        self.rect.y = int(self.y)
        self.rect.x += int(math.sin(self.wobble_phase) * 1.2)

    @property
    def is_off_screen(self):
        return self.rect.top > self.screen_rect.bottom
