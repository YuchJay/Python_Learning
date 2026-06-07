"""程序化音效管理器 —— 无需外部音频文件，通过波形合成生成所有音效。"""
import io
import math
import random
import struct
import wave

import pygame


class SoundManager:
    """管理所有游戏音效的生成、缓存和播放。"""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self._cache = {}
        self._sample_rate = 22050

    def toggle(self):
        """切换音效开关"""
        self.enabled = not self.enabled
        return self.enabled

    def _make_wav(self, generator, duration):
        """将采样生成器函数渲染为pygame Sound对象。"""
        n_samples = int(self._sample_rate * duration)
        buf = io.BytesIO()
        with wave.open(buf, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self._sample_rate)
            for i in range(n_samples):
                t = i / self._sample_rate
                envelope = max(0.0, 1.0 - i / n_samples)  # 线性衰减包络
                val = generator(t) * envelope
                val = max(-1.0, min(1.0, val))
                wf.writeframes(struct.pack('<h', int(val * 32767)))
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _cached(self, key, gen_func, duration):
        """从缓存获取音效，首次调用时生成并缓存。"""
        if key not in self._cache:
            self._cache[key] = self._make_wav(gen_func, duration)
        return self._cache[key]

    # ── 音效定义 ──────────────────────────────────────────

    def play_shoot(self):
        """发射子弹：短促的上升啁啾声"""
        if not self.enabled:
            return
        def gen(t):
            freq = 800 + 2000 * t / 0.08  # 频率从800Hz升到2800Hz
            return math.sin(2 * math.pi * freq * t) * 0.3
        self._cached('shoot', gen, 0.08).play()

    def play_explosion(self):
        """外星人爆炸：白噪声衰减"""
        if not self.enabled:
            return
        def gen(t):
            return random.uniform(-1, 1) * 0.35
        self._cached('explosion', gen, 0.18).play()

    def play_big_explosion(self):
        """大型爆炸（Boss死亡）：更长更响的噪声 + 低频轰隆"""
        if not self.enabled:
            return
        def gen(t):
            noise = random.uniform(-1, 1) * 0.4
            rumble = math.sin(2 * math.pi * 60 * t) * 0.5  # 60Hz低频
            return noise * 0.7 + rumble * 0.3
        self._cached('big_explosion', gen, 0.35).play()

    def play_hit(self):
        """飞船被击中：低沉撞击声"""
        if not self.enabled:
            return
        def gen(t):
            return math.sin(2 * math.pi * 150 * t) * 0.5
        self._cached('hit', gen, 0.25).play()

    def play_powerup(self):
        """拾取道具：上升琶音"""
        if not self.enabled:
            return
        def gen(t):
            # 三段上升音
            if t < 0.08:
                freq = 600
            elif t < 0.16:
                freq = 900
            else:
                freq = 1200
            return math.sin(2 * math.pi * freq * t) * 0.3
        self._cached('powerup', gen, 0.24).play()

    def play_level_up(self):
        """升级：欢快的三音符上行"""
        if not self.enabled:
            return
        def gen(t):
            if t < 0.10:
                freq = 523   # C5
            elif t < 0.20:
                freq = 659   # E5
            elif t < 0.30:
                freq = 784   # G5
            else:
                freq = 1047  # C6
            return math.sin(2 * math.pi * freq * t) * 0.3
        self._cached('level_up', gen, 0.40).play()

    def play_game_over(self):
        """游戏结束：下行悲伤旋律"""
        if not self.enabled:
            return
        def gen(t):
            if t < 0.15:
                freq = 440
            elif t < 0.30:
                freq = 370
            elif t < 0.45:
                freq = 311
            else:
                freq = 262
            return math.sin(2 * math.pi * freq * t) * 0.35
        self._cached('game_over', gen, 0.60).play()

    def play_combo(self):
        """连击提示：叮的一声"""
        if not self.enabled:
            return
        def gen(t):
            return math.sin(2 * math.pi * 1200 * t) * 0.25
        self._cached('combo', gen, 0.10).play()

    def play_shield_break(self):
        """护盾破裂：碎裂声"""
        if not self.enabled:
            return
        def gen(t):
            return random.uniform(-1, 1) * 0.3
        self._cached('shield_break', gen, 0.12).play()
