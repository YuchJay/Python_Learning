"""浮动文字 —— 击杀得分弹出和连击提示。"""
import random
import pygame


class FloatingText:
    """单条浮动文字 —— 向上飘起并逐渐淡出。"""

    def __init__(self, x, y, text, color, font_size=24, duration=45):
        self.x = float(x)
        self.y = float(y)
        self.duration = duration
        self.max_duration = duration

        font = pygame.font.SysFont(None, font_size)
        self.image = font.render(text, True, color)
        self.rect = self.image.get_rect(center=(int(x), int(y)))

        # 随机水平偏移，避免重叠
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = -1.5  # 向上飘

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.duration -= 1
        self.rect.center = (int(self.x), int(self.y))

        # 逐渐淡出
        if self.duration < self.max_duration * 0.3:
            alpha = int(255 * self.duration / (self.max_duration * 0.3))
            self.image.set_alpha(max(0, alpha))

    @property
    def is_dead(self):
        return self.duration <= 0


class FloatingTextManager:
    """管理所有浮动文字的更新和绘制。"""

    def __init__(self):
        self.texts = []

    def add_score(self, x, y, points):
        """在指定位置显示得分数。"""
        color = (255, 255, 100) if points >= 100 else (255, 255, 200)
        size = 28 if points >= 100 else 20
        self.texts.append(FloatingText(x, y, f"+{points}", color, size))

    def add_combo(self, x, y, combo_count):
        """在指定位置显示连击提示。"""
        colors = {
            5: (255, 200, 50),    # 5连击: 金色
            10: (255, 100, 50),   # 10连击: 橙红
            15: (255, 50, 100),   # 15连击: 粉红
            20: (255, 50, 255),   # 20连击: 紫红
        }
        color = (200, 200, 255)
        size = 30
        for threshold, c in sorted(colors.items(), reverse=True):
            if combo_count >= threshold:
                color = c
                size = 36
                break

        self.texts.append(FloatingText(
            x, y - 30, f"COMBO x{combo_count}!", color, size, duration=60))

    def add_pickup(self, x, y, label, color):
        """在指定位置显示拾取道具提示。"""
        self.texts.append(FloatingText(
            x, y - 20, label, color, font_size=28, duration=50))

    def update(self):
        for t in self.texts:
            t.update()
        self.texts = [t for t in self.texts if not t.is_dead]

    def draw(self, screen):
        for t in self.texts:
            screen.blit(t.image, t.rect)
