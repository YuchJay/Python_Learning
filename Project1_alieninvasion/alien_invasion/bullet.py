"""子弹类 —— 支持直线和斜向射击（散射道具用）。"""
import math
import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    """管理飞船所发射子弹的类。"""

    def __init__(self, ai_game, angle=0):
        """在飞船当前位置创建一个子弹对象。
        angle: 偏转角（度），0=直上，正值=右偏，负值=左偏。
        """
        super().__init__()
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color
        self.angle = math.radians(angle)  # 转为弧度

        # 创建子弹Surface图像
        self.image = pygame.Surface(
            (self.settings.bullet_width, self.settings.bullet_height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.midtop = ai_game.ship.rect.midtop

        # 存储精确浮点位置
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # 计算速度分量
        speed = self.settings.bullet_speed
        self.vx = math.sin(self.angle) * speed
        self.vy = -math.cos(self.angle) * speed

    def update(self):
        """更新子弹位置。"""
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
