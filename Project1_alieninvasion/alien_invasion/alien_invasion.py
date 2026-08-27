"""Alien Invasion —— Multi-Language Edition.

ARCHITECTURE (4 languages across 3 compilation strategies):
  Python   (interpreted)  → Game logic, menus, sprites, events
  Cython   (AOT compiled) → Starfield renderer, particle system, sound engine
  C        (native via FFI)→ Raw WAV sample buffer generation (tightest loop)
  Numba    (JIT compiled)  → Batch physics kernels (star twinkle, particles)
"""
import math
import random
import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from ship import Ship
from bullet import Bullet
from alien import Alien
from powerup import PowerUp, PowerUpType
from floating_text import FloatingTextManager
from menu import MenuScreen

# ── Multi-Language Engine imports (with pure-Python fallbacks) ──
from engine import (StarfieldEngine, SoundEngine, print_engine_status)
from engine import ExplosionParticle, create_explosion as _engine_create_explosion


class AlienInvasion:
    """管理游戏所有资源、状态和行为的核心类。"""

    def __init__(self):
        pygame.init()
        pygame.mixer.init(buffer=512)  # 小缓冲减少音效延迟
        self.settings = Settings()

        # 窗口：尝试vsync，旧版pygame回退
        try:
            self.screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN, vsync=1)
        except TypeError:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        self.screen_rect = self.screen.get_rect()
        pygame.display.set_caption("Alien Invasion")

        # ── 帧率控制 ─────────────────────────────────
        self.clock = pygame.time.Clock()

        # ── 音效（C引擎：优先C DLL→Cython原生→Python回退）───
        self.sound = SoundEngine(enabled=self.settings.sound_enabled)

        # ── 星空背景（Cython引擎：预分配表面池，有Python回退）──
        self.starfield = StarfieldEngine(
            self.settings.screen_width, self.settings.screen_height)

        # ── 游戏状态 ─────────────────────────────────
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # ── 精灵与编组 ───────────────────────────────
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()   # 粒子爆炸
        self.powerups = pygame.sprite.Group()     # 掉落道具

        # ── 浮动文字 ─────────────────────────────────
        self.float_text = FloatingTextManager()

        # ── 道具计时器（过期时间戳，毫秒；0=未激活）────
        self.powerup_timers = {
            'rapid_fire': 0,
            'shield': 0,
            'spread_shot': 0,
        }

        # ── 连击追踪 ─────────────────────────────────
        self.combo_count = 0
        self.last_kill_time = 0.0  # pygame ticks in seconds

        # ── 屏幕震动 ─────────────────────────────────
        self.shake_frames = 0
        self.shake_offset = (0, 0)

        # ── 主菜单 ───────────────────────────────────
        self.menu = MenuScreen(self)

        # ── 共用字体 ──────────────────────────────────
        self._sound_status_font = pygame.font.SysFont(None, 28)

        # 鼠标默认可见（菜单中需要）
        pygame.mouse.set_visible(True)

        # 报告多语言引擎状态（首次启动时打印一次）
        print_engine_status()

    # ═══════════════════════════════════════════════════════════
    #  退出 & 工具
    # ═══════════════════════════════════════════════════════════

    def _quit_game(self):
        """安全退出：保存最高分后退出。"""
        self.stats.save_high_score()
        sys.exit()

    # ═══════════════════════════════════════════════════════════
    #  外星人舰队管理
    # ═══════════════════════════════════════════════════════════

    def _create_fleet(self):
        """创建外星人舰队（布局+随机精英+Boss）。"""
        alien = Alien(self, alien_type=Alien.TYPE_NORMAL)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = max(1, available_space_x // (2 * alien_width))

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height
                             - (3 * alien_height) - ship_height)
        number_rows = max(1, available_space_y // (2 * alien_height))

        # 确定Boss位置（如果当前等级满足条件）
        boss_pos = None
        if self.stats.level >= self.settings.boss_alien_level_start:
            boss_col = random.randint(0, number_aliens_x - 1)
            boss_row = random.randint(0, number_rows - 1)
            boss_pos = (boss_col, boss_row)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                # Boss占据一个位置
                if boss_pos and (alien_number, row_number) == boss_pos:
                    alien_type = Alien.TYPE_BOSS
                else:
                    alien_type = None  # 由Alien内部随机决定普通/精英
                self._create_alien(alien_number, row_number, alien_type)

    def _create_alien(self, alien_number, row_number, alien_type=None):
        """创建一个外星人并放入舰队。"""
        alien = Alien(self, alien_type=alien_type)
        alien_width = alien.rect.width
        alien_height = alien.rect.height
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = int(alien.x)
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """检测是否有外星人触及屏幕边缘。"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """全体外星人下移并反转方向。"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    # ═══════════════════════════════════════════════════════════
    #  道具系统
    # ═══════════════════════════════════════════════════════════

    def _try_drop_powerup(self, x, y):
        """以一定概率在指定位置生成随机道具。"""
        if random.random() < self.settings.powerup_drop_chance:
            powerup = PowerUp(self, x, y)
            self.powerups.add(powerup)

    def _update_powerups(self):
        """更新道具位置，检查与飞船的碰撞。"""
        self.powerups.update()

        # 移除掉出屏幕的道具
        for p in self.powerups.copy():
            if p.is_off_screen:
                self.powerups.remove(p)

        # 检测飞船与道具的碰撞
        collisions = pygame.sprite.spritecollide(self.ship, self.powerups, True)
        for powerup in collisions:
            self._apply_powerup(powerup)
            self.sound.play_powerup()

    def _apply_powerup(self, powerup):
        """激活道具效果。"""
        now = pygame.time.get_ticks()
        ptype = powerup.power_type

        if ptype == PowerUpType.EXTRA_LIFE:
            self.stats.ships_left = min(
                self.stats.ships_left + 1, self.settings.ship_limit + 2)
            self.sb.prep_ships()
            self.float_text.add_pickup(
                self.ship.rect.centerx, self.ship.rect.top,
                "EXTRA LIFE!", (0, 255, 80))
        elif ptype == PowerUpType.RAPID_FIRE:
            duration_ms = int(self.settings.powerup_rapid_fire_duration * 1000)
            self.powerup_timers['rapid_fire'] = now + duration_ms
            self.float_text.add_pickup(
                self.ship.rect.centerx, self.ship.rect.top,
                "RAPID FIRE!", (255, 80, 0))
        elif ptype == PowerUpType.SHIELD:
            duration_ms = int(self.settings.powerup_shield_duration * 1000)
            self.powerup_timers['shield'] = now + duration_ms
            self.float_text.add_pickup(
                self.ship.rect.centerx, self.ship.rect.top,
                "SHIELD!", (0, 180, 255))
        elif ptype == PowerUpType.SPREAD_SHOT:
            duration_ms = int(self.settings.powerup_spread_shot_duration * 1000)
            self.powerup_timers['spread_shot'] = now + duration_ms
            self.float_text.add_pickup(
                self.ship.rect.centerx, self.ship.rect.top,
                "SPREAD SHOT!", (255, 220, 0))

    def _update_powerup_timers(self):
        """清除已过期的道具效果。"""
        now = pygame.time.get_ticks()
        for key in list(self.powerup_timers.keys()):
            if self.powerup_timers[key] and now >= self.powerup_timers[key]:
                if key == 'shield':
                    self.sound.play_shield_break()
                self.powerup_timers[key] = 0

    @property
    def _has_rapid_fire(self):
        return self.powerup_timers['rapid_fire'] > pygame.time.get_ticks()

    @property
    def _has_shield(self):
        return self.powerup_timers['shield'] > pygame.time.get_ticks()

    @property
    def _has_spread_shot(self):
        return self.powerup_timers['spread_shot'] > pygame.time.get_ticks()

    # ═══════════════════════════════════════════════════════════
    #  事件处理
    # ═══════════════════════════════════════════════════════════

    def _check_events(self):
        """响应所有输入事件。"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()

            # 游戏非活跃时，由菜单接管键盘/鼠标事件
            if not self.stats.game_active:
                consumed = self.menu.handle_event(event)
                if consumed:
                    continue
                # 如果菜单未消费该事件（如 KEYUP），继续处理
                if event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    consumed = self.menu.handle_event(event)
                continue

            # 游戏活跃时正常处理
            if event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _start_new_game(self):
        """初始化新游戏状态。"""
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.stats.games_played += 1
        self.stats.game_active = True
        self.stats.game_paused = False
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # 清空所有内容
        self.aliens.empty()
        self.bullets.empty()
        self.explosions.empty()
        self.powerups.empty()
        self.float_text.texts.clear()

        # 重置道具计时器
        for key in self.powerup_timers:
            self.powerup_timers[key] = 0

        # 重置连击
        self.combo_count = 0
        self.last_kill_time = 0.0
        self.shake_frames = 0

        # 重建世界
        self._create_fleet()
        self.ship.center_ship()

        # 刷新菜单文本（下次返回菜单时显示 "PLAY AGAIN" 而不是 "START GAME"）
        self.menu.refresh_items()

        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """按键按下事件。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._quit_game()
        elif event.key == pygame.K_ESCAPE:
            # 返回主菜单
            if self.stats.game_active:
                self.stats.game_active = False
                self.menu.refresh_items()
                pygame.mouse.set_visible(True)
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            if self.stats.game_active:
                self.stats.game_paused = not self.stats.game_paused
        elif event.key == pygame.K_m:
            # 切换音效
            enabled = self.sound.toggle()
            self.settings.sound_enabled = enabled

    def _check_keyup_events(self, event):
        """按键释放事件。"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    # ═══════════════════════════════════════════════════════════
    #  射击系统
    # ═══════════════════════════════════════════════════════════

    def _fire_bullet(self):
        """发射子弹（考虑道具效果：速射、散射）。"""
        effective_limit = self.settings.bullets_allowed
        if self._has_rapid_fire:
            effective_limit *= 2  # 速射时翻倍弹药

        # 散射需要3发子弹的空间
        needed = 3 if self._has_spread_shot else 1
        if len(self.bullets) + needed > effective_limit:
            return

        if self._has_spread_shot:
            # 散射：3发子弹呈扇形
            self._create_bullet(angle=0)       # 正上方
            self._create_bullet(angle=-12)     # 左偏
            self._create_bullet(angle=12)      # 右偏
        else:
            self._create_bullet(angle=0)

        self.sound.play_shoot()

    def _create_bullet(self, angle=0):
        """创建子弹（不检查弹药限制，由调用方 _fire_bullet 负责检查）。"""
        bullet = Bullet(self, angle=angle)
        self.bullets.add(bullet)

    # ═══════════════════════════════════════════════════════════
    #  子弹更新 & 碰撞
    # ═══════════════════════════════════════════════════════════

    def _update_bullets(self):
        """更新子弹位置，清理越界的，检测碰撞。"""
        self.bullets.update()

        # 删除飞出屏幕的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
            elif hasattr(bullet, 'rect') and bullet.rect.left <= 0:
                self.bullets.remove(bullet)
            elif bullet.rect.right >= self.settings.screen_width:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """子弹与外星人碰撞（支持多血条敌人）。"""
        # 使用 False, False 手动控制删除逻辑
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, False, False)

        if not collisions:
            return

        for bullet, aliens_hit in collisions.items():
            # 子弹只命中一个外星人（取最近碰撞的）
            if not aliens_hit:
                continue
            alien = aliens_hit[0]

            # 移除子弹
            if bullet in self.bullets:
                self.bullets.remove(bullet)

            # 造成伤害
            if alien.take_damage():
                # 外星人死亡
                self.aliens.remove(alien)
                self._on_alien_killed(alien)
            # 否则外星人受伤但未死（Boss），子弹已消耗

    def _on_alien_killed(self, alien):
        """外星人被击杀后的所有响应。"""
        cx, cy = alien.rect.centerx, alien.rect.centery

        # ── 爆炸粒子 ─────────────────────────────
        self._spawn_explosion(cx, cy, alien)

        # ── 音效 ─────────────────────────────────
        if alien.alien_type == Alien.TYPE_BOSS:
            self.sound.play_big_explosion()
        else:
            self.sound.play_explosion()

        # ── 连击系统 ─────────────────────────────
        now_sec = pygame.time.get_ticks() / 1000.0
        if now_sec - self.last_kill_time < self.settings.combo_timeout:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.last_kill_time = now_sec

        # 计算得分（含连击奖励）
        combo_bonus = self.combo_count * self.settings.combo_score_bonus_per_level
        total_points = alien.points + combo_bonus
        self.stats.score += total_points

        # ── 浮动文字 ─────────────────────────────
        self.float_text.add_score(cx, cy - 10, total_points)
        if self.combo_count >= 5 and self.combo_count % 5 == 0:
            self.float_text.add_combo(cx, cy - 40, self.combo_count)
            self.sound.play_combo()

        # ── 更新记分牌 ───────────────────────────
        self.sb.prep_score()
        self.sb.check_high_score()

        # ── 道具掉落 ─────────────────────────────
        self._try_drop_powerup(cx, cy)

    def _spawn_explosion(self, cx, cy, alien):
        """生成爆炸粒子效果（Cython引擎优先，Python回退）。"""
        # Use engine factory function when available (Cython optimized)
        if _engine_create_explosion is not None:
            particles = _engine_create_explosion(cx, cy, alien.alien_type)
            for p in particles:
                self.explosions.add(p)
        else:
            # Pure Python fallback
            if alien.alien_type == Alien.TYPE_BOSS:
                colors = [(255, 200, 50), (255, 150, 30), (255, 100, 20), (255, 50, 10)]
                for _ in range(40):
                    color = random.choice(colors)
                    p = ExplosionParticle(cx, cy, color)
                    p.size = random.randint(5, 12)
                    p.life = random.randint(20, 45)
                    p.max_life = p.life
                    self.explosions.add(p)
            elif alien.alien_type == Alien.TYPE_ELITE:
                colors = [(255, 80, 80), (255, 50, 50), (255, 150, 50)]
                for _ in range(20):
                    p = ExplosionParticle(cx, cy, random.choice(colors))
                    self.explosions.add(p)
            else:
                colors = [(100, 200, 100), (150, 255, 150), (200, 255, 200)]
                for _ in range(12):
                    p = ExplosionParticle(cx, cy, random.choice(colors))
                    self.explosions.add(p)

        # ── 检查是否清空舰队 ─────────────────────
        if not self.aliens:
            self._on_fleet_cleared()

    def _on_fleet_cleared(self):
        """所有外星人被消灭后的处理。"""
        self.bullets.empty()
        self.powerups.empty()
        self.settings.increase_speed()
        self.stats.level += 1
        self.sb.prep_level()
        self.sound.play_level_up()
        self._create_fleet()

    # ═══════════════════════════════════════════════════════════
    #  外星人更新 & 碰撞
    # ═══════════════════════════════════════════════════════════

    def _update_aliens(self):
        """更新外星人位置、检测边缘、检测与飞船的碰撞。"""
        self._check_fleet_edges()
        self.aliens.update()

        # 外星人与飞船碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 外星人到达屏幕底部
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达屏幕底部。"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        """飞船被击中（外星人碰撞或到达底部）。"""
        # 护盾激活时免疫伤害
        if self._has_shield:
            return

        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # 清空场景
            self.aliens.empty()
            self.bullets.empty()
            self.explosions.empty()
            self.powerups.empty()

            # 重置道具
            for key in self.powerup_timers:
                self.powerup_timers[key] = 0

            # 重建
            self._create_fleet()
            self.ship.center_ship()

            # 震动 + 音效
            self.shake_frames = self.settings.screen_shake_duration
            self.sound.play_hit()

            sleep(0.5)
        else:
            self.stats.game_active = False
            self.sound.play_game_over()
            self.menu.refresh_items()
            pygame.mouse.set_visible(True)

    # ═══════════════════════════════════════════════════════════
    #  主循环
    # ═══════════════════════════════════════════════════════════

    def run_game(self):
        """游戏主循环。"""
        while True:
            dt = self.clock.tick(self.settings.fps) / 1000.0

            self._check_events()

            if self.stats.game_active and not self.stats.game_paused:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_powerups()
                self._update_powerup_timers()
                self.explosions.update()
                self.float_text.update()
                self.starfield.update()

                # 屏幕震动倒计时
                if self.shake_frames > 0:
                    self.shake_frames -= 1
            elif not self.stats.game_active:
                # 主菜单更新（星空动画）
                self.menu.update(dt)

            self._update_screen()

    # ═══════════════════════════════════════════════════════════
    #  渲染
    # ═══════════════════════════════════════════════════════════

    def _update_screen(self):
        """渲染整个画面。"""
        # ── 游戏非活跃时，展示主菜单 ──────────
        if not self.stats.game_active:
            self.menu.draw()
            pygame.display.flip()
            return

        # ── 屏幕震动偏移 ──────────────────────
        if self.shake_frames > 0:
            intensity = self.settings.screen_shake_intensity
            ox = random.randint(-intensity, intensity)
            oy = random.randint(-intensity, intensity)
        else:
            ox, oy = 0, 0

        # ── 星空背景 ─────────────────────────────
        self.screen.fill(self.settings.bg_color)
        self.starfield.draw(self.screen)

        # ── 游戏元素（应用震动偏移）─────────────
        if ox != 0 or oy != 0:
            game_surf = pygame.Surface(
                (self.settings.screen_width, self.settings.screen_height))
            game_surf.fill(self.settings.bg_color)
            self._draw_game_objects(game_surf)
            self.screen.blit(game_surf, (ox, oy))
        else:
            self._draw_game_objects(self.screen)

        # ── UI层（不受震动影响）─────────────────
        self.sb.show_score()

        if self.stats.game_paused:
            self._draw_pause_overlay()

        # ── 音效状态指示器 ─────────────────────
        self._draw_sound_indicator()

        # ── 道具计时器条 ───────────────────────
        if not self.stats.game_paused:
            self._draw_powerup_timers()

        pygame.display.flip()

    def _draw_game_objects(self, surface):
        """绘制所有游戏对象到指定表面。"""
        self.ship.blitme()
        self.bullets.draw(surface)
        self.aliens.draw(surface)
        self.explosions.draw(surface)
        self.powerups.draw(surface)
        self.float_text.draw(surface)

        # 护盾视觉（围绕飞船的发光环）
        if self._has_shield:
            self._draw_shield(surface)

    def _draw_shield(self, surface):
        """绘制护盾效果：围绕飞船的半透明光环。"""
        center = self.ship.rect.center
        radius = max(self.ship.rect.width, self.ship.rect.height) // 2 + 10

        # 脉冲效果
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
        alpha = int(80 + 60 * pulse)

        shield_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (0, 180, 255, alpha),
                           (radius, radius), radius)
        pygame.draw.circle(shield_surf, (0, 220, 255, alpha // 2),
                           (radius, radius), radius - 3, 3)
        surface.blit(shield_surf,
                     (center[0] - radius, center[1] - radius))

    def _draw_pause_overlay(self):
        """绘制暂停覆盖层。"""
        overlay = pygame.Surface(
            (self.settings.screen_width, self.settings.screen_height),
            pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        pause_font = pygame.font.SysFont(None, 72)
        pause_img = pause_font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_img.get_rect(center=self.screen_rect.center)
        self.screen.blit(pause_img, pause_rect)

        hint_font = pygame.font.SysFont(None, 36)
        hint_img = hint_font.render(
            "P = Resume  |  M = Sound  |  ESC = Menu", True, (200, 200, 200))
        hint_rect = hint_img.get_rect(
            centerx=self.screen_rect.centerx, top=pause_rect.bottom + 20)
        self.screen.blit(hint_img, hint_rect)

    def _draw_sound_indicator(self):
        """绘制音效状态指示器（右下角）。"""
        text = "🔊 Sound ON" if self.settings.sound_enabled else "🔇 Sound OFF"
        color = (150, 150, 150)
        img = self._sound_status_font.render(text, True, color)
        rect = img.get_rect()
        rect.bottomright = (self.screen_rect.right - 10,
                            self.screen_rect.bottom - 10)
        self.screen.blit(img, rect)

    def _draw_powerup_timers(self):
        """绘制当前激活道具的剩余时间条。"""
        now = pygame.time.get_ticks()
        bar_width = 160
        bar_height = 8
        bar_x = 10
        bar_y = self.screen_rect.bottom - 50

        active_bars = []
        for key, expire_ts in self.powerup_timers.items():
            if expire_ts and now < expire_ts:
                remaining = (expire_ts - now) / 1000.0
                if key == 'rapid_fire':
                    total = self.settings.powerup_rapid_fire_duration
                    label = 'RAPID FIRE'
                    color = (255, 80, 0)
                elif key == 'shield':
                    total = self.settings.powerup_shield_duration
                    label = 'SHIELD'
                    color = (0, 180, 255)
                elif key == 'spread_shot':
                    total = self.settings.powerup_spread_shot_duration
                    label = 'SPREAD'
                    color = (255, 220, 0)
                else:
                    continue
                ratio = remaining / total
                active_bars.append((label, color, ratio, remaining))

        for i, (label, color, ratio, remaining) in enumerate(active_bars):
            y = bar_y - i * (bar_height + 14)

            # 标签
            lbl = self._sound_status_font.render(label, True, color)
            self.screen.blit(lbl, (bar_x, y - 10))

            # 进度条背景
            bg_rect = pygame.Rect(bar_x, y + 14, bar_width, bar_height)
            pygame.draw.rect(self.screen, (60, 60, 60), bg_rect)

            # 进度条填充
            fill_rect = pygame.Rect(bar_x, y + 14, int(bar_width * ratio), bar_height)
            pygame.draw.rect(self.screen, color, fill_rect)

            # 剩余秒数
            sec_text = self._sound_status_font.render(
                f"{remaining:.1f}s", True, color)
            self.screen.blit(sec_text, (bar_x + bar_width + 8, y + 8))


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
