"""粒子爆炸效果 —— 外星人被摧毁时的视觉反馈。"""
import math
import random
import pygame
from pygame.sprite import Sprite


class Particle(Sprite):
    """单个粒子 —— 从爆炸中心向外飞散，逐渐缩小并消失。"""

    def __init__(self, x, y, color):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.color = color

        # 随机方向和速度
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(1.5, 5.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # 生命（帧数）
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.size = random.randint(3, 7)

        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self._render()

    def _render(self):
        """重新绘制粒子表面（随生命衰减而缩小变淡）。"""
        self.image.fill((0, 0, 0, 0))
        alpha = int(255 * self.life / self.max_life)
        current_size = max(1, int(self.size * self.life / self.max_life))
        color_with_alpha = (*self.color, alpha)
        center = self.image.get_width() // 2
        pygame.draw.circle(self.image, color_with_alpha, (center, center), current_size)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # 微重力，粒子缓缓下落
        self.rect.center = (int(self.x), int(self.y))
        self.life -= 1
        if self.life > 0:
            self._render()

    @property
    def is_dead(self):
        return self.life <= 0

