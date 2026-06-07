"""星空背景 —— 多层视差滚动星空，营造太空深度感。"""
import math
import random
import pygame


class Star:
    """单颗星星 —— 带闪烁和深度属性。"""
    __slots__ = ('x', 'y', 'size', 'speed', 'brightness', 'twinkle_offset', 'twinkle_speed')

    def __init__(self, screen_width, screen_height, layer):
        self.x = random.uniform(0, screen_width)
        self.y = random.uniform(0, screen_height)

        # 三个深度层：远（小、慢、暗）、中、近（大、快、亮）
        if layer == 0:  # 远层
            self.size = random.uniform(0.5, 1.5)
            self.speed = random.uniform(0.2, 0.5)
            self.brightness = random.randint(60, 120)
        elif layer == 1:  # 中层
            self.size = random.uniform(1.0, 2.5)
            self.speed = random.uniform(0.5, 1.2)
            self.brightness = random.randint(100, 180)
        else:  # 近层
            self.size = random.uniform(1.5, 3.5)
            self.speed = random.uniform(1.0, 2.0)
            self.brightness = random.randint(140, 230)

        self.twinkle_offset = random.uniform(0, 6.28)
        self.twinkle_speed = random.uniform(0.02, 0.06)


class Starfield:
    """管理多层星空背景的绘制与滚动。"""

    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.layers = []
        for layer in range(3):
            stars = [Star(screen_width, screen_height, layer)
                     for _ in range(60 if layer == 0 else 30)]
            self.layers.append(stars)

    def update(self):
        """所有星星向下滚动，超出屏幕的从顶部重新出现。"""
        for stars in self.layers:
            for star in stars:
                star.y += star.speed
                star.twinkle_offset += star.twinkle_speed
                if star.y > self.height:
                    star.y = random.uniform(-10, 0)
                    star.x = random.uniform(0, self.width)

    def draw(self, screen, frame_count=0):
        """将所有层的星星绘制到屏幕上。"""
        for stars in self.layers:
            for star in stars:
                # 闪烁：亮度随正弦波变化
                flicker = (math.sin(star.twinkle_offset) + 1) / 2  # 0~1
                alpha = int(star.brightness * (0.5 + 0.5 * flicker))
                alpha = max(0, min(255, alpha))
                color = (alpha, alpha, alpha)

                if star.size <= 1.5:
                    screen.set_at((int(star.x), int(star.y)), color)
                else:
                    radius = max(1, int(star.size))
                    # 用带透明度的表面绘制光晕
                    surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
                    pygame.draw.circle(surf, (*color, alpha),
                                       (radius * 2, radius * 2), radius)
                    screen.blit(surf, (int(star.x) - radius * 2,
                                       int(star.y) - radius * 2),
                                special_flags=pygame.BLEND_ADD)
