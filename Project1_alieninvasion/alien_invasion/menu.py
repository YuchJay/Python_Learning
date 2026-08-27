"""主菜单界面 —— 带动画标题、菜单项导航和星空背景。"""
import math
import pygame


class MenuItem:
    """菜单中单个可选条目 —— 支持悬停高亮和点击检测。"""

    def __init__(self, text, center, font, color_normal=(180, 180, 200),
                 color_selected=(255, 255, 100)):
        self.text = text
        self.font = font
        self.color_normal = color_normal
        self.color_selected = color_selected

        # 渲染两次（普通态和选中态）
        self.image_normal = font.render(text, True, color_normal)
        self.image_selected = font.render(text, True, color_selected)
        self.image = self.image_normal
        self.rect = self.image.get_rect(center=center)

        self.base_center = center  # 记住原始位置用于动画
        self.hover_timer = 0.0

    def update(self, selected, dt):
        """更新选中状态和悬停动画计时器。"""
        self.image = self.image_selected if selected else self.image_normal
        self.rect = self.image.get_rect(center=self.base_center)
        if selected:
            self.hover_timer += dt
        else:
            self.hover_timer = 0.0


class MenuScreen:
    """管理主菜单的所有渲染和交互。"""

    def __init__(self, ai_game):
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen_rect
        self.settings = ai_game.settings
        self.starfield = ai_game.starfield
        self.stats = ai_game.stats
        self.sound_manager = ai_game.sound

        # ── 字体 ─────────────────────────────────────
        self.title_font = pygame.font.SysFont(None, 100)
        self.item_font = pygame.font.SysFont(None, 52)
        self.info_font = pygame.font.SysFont(None, 30)
        self.credits_font = pygame.font.SysFont(None, 24)

        # ── 标题位置 ─────────────────────────────────
        self.title_base_y = self.screen_rect.centery - 160

        # ── 菜单项列表 ───────────────────────────────
        self._build_items()

        # ── 选中索引 ─────────────────────────────────
        self.selected_index = 0

        # ── 动画计时器 ───────────────────────────────
        self._start_ticks = pygame.time.get_ticks()

        # ── 高亮指示器（选中项左侧的箭头）────────────
        self._arrow_font = pygame.font.SysFont(None, 44)
        self._arrow_image = self._arrow_font.render("▶", True, (255, 255, 100))

    def _build_items(self):
        """（重新）构建菜单项列表 —— 当选项文本需要刷新时调用。"""
        base_y = self.screen_rect.centery - 20
        spacing = 60

        labels = self._get_item_labels()
        self.items = []
        for i, label in enumerate(labels):
            center = (self.screen_rect.centerx, base_y + i * spacing)
            self.items.append(MenuItem(label, center, self.item_font))

    def _get_item_labels(self):
        """根据当前游戏状态返回菜单项文本列表。"""
        sound_status = "ON" if self.settings.sound_enabled else "OFF"

        if self.stats.games_played > 0:
            # 至少玩过一局
            return [
                "PLAY AGAIN",
                f"SOUND: {sound_status}",
                "QUIT",
            ]
        else:
            # 首次启动
            return [
                "START GAME",
                f"SOUND: {sound_status}",
                "QUIT",
            ]

    def refresh_items(self):
        """在状态改变后（如音效切换）刷新菜单文本。"""
        old_index = self.selected_index
        self._build_items()
        self.selected_index = min(old_index, len(self.items) - 1)

    # ═══════════════════════════════════════════════════════════
    #  事件处理
    # ═══════════════════════════════════════════════════════════

    def handle_event(self, event):
        """处理菜单输入事件，返回 True 表示事件已被消费。"""
        if event.type == pygame.KEYDOWN:
            return self._handle_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_hover(event.pos)
        return False

    def _handle_key(self, event):
        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.items)
            return True
        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.items)
            return True
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            self._activate()
            return True
        elif event.key == pygame.K_ESCAPE:
            self._activate_quit()
            return True
        return False

    def _handle_click(self, pos):
        """检查鼠标是否点击了某个菜单项。"""
        for i, item in enumerate(self.items):
            if item.rect.collidepoint(pos):
                self.selected_index = i
                self._activate()
                return True
        return False

    def _handle_hover(self, pos):
        """鼠标悬停时自动高亮对应菜单项。"""
        for i, item in enumerate(self.items):
            if item.rect.collidepoint(pos):
                self.selected_index = i
                return True
        return False

    def _activate(self):
        """触发当前选中菜单项的功能。"""
        item = self.items[self.selected_index]
        label = self.items[self.selected_index].text

        if label.startswith("START GAME") or label.startswith("PLAY AGAIN"):
            self.ai_game._start_new_game()
        elif label.startswith("SOUND"):
            enabled = self.sound_manager.toggle()
            self.settings.sound_enabled = enabled
            self.refresh_items()
        elif label.startswith("QUIT"):
            self._activate_quit()

    def _activate_quit(self):
        """退出游戏。"""
        self.ai_game._quit_game()

    # ═══════════════════════════════════════════════════════════
    #  更新
    # ═══════════════════════════════════════════════════════════

    def update(self, dt):
        """更新菜单动画和星空背景。"""
        self.starfield.update()
        for i, item in enumerate(self.items):
            item.update(i == self.selected_index, dt)

    # ═══════════════════════════════════════════════════════════
    #  渲染
    # ═══════════════════════════════════════════════════════════

    def draw(self):
        """完整绘制菜单画面。"""
        # 背景
        self.screen.fill(self.settings.bg_color)
        self.starfield.draw(self.screen)

        # ── 标题（带脉动动画）─────────────────────
        self._draw_title()

        # ── 菜单项 ─────────────────────────────────
        self._draw_items()

        # ── 高分展示 ───────────────────────────────
        self._draw_high_score()

        # ── 底部提示 ───────────────────────────────
        self._draw_footer()

    def _draw_title(self):
        """绘制带发光效果和脉动动画的标题。"""
        elapsed = (pygame.time.get_ticks() - self._start_ticks) / 1000.0

        # 脉动缩放
        pulse = 1.0 + math.sin(elapsed * 1.5) * 0.03

        # 外发光（大号模糊文字）
        glow_sizes = [104, 108]
        for size in glow_sizes:
            glow_font = pygame.font.SysFont(None, int(size * pulse))
            glow_img = glow_font.render("ALIEN INVASION", True, (80, 80, 180))
            glow_rect = glow_img.get_rect(
                centerx=self.screen_rect.centerx, centery=self.title_base_y)
            self.screen.blit(glow_img, glow_rect)

        # 主标题
        title_font = pygame.font.SysFont(None, int(100 * pulse))
        title_img = title_font.render("ALIEN INVASION", True, (200, 220, 255))
        title_rect = title_img.get_rect(
            centerx=self.screen_rect.centerx, centery=self.title_base_y)
        self.screen.blit(title_img, title_rect)

    def _draw_items(self):
        """绘制所有菜单项（选中项带箭头指示器和高亮）。"""
        for i, item in enumerate(self.items):
            # 选中项的箭头动画
            if i == self.selected_index:
                wobble = math.sin(item.hover_timer * 3.0) * 4
                arrow_x = item.rect.left - 30 + wobble
                arrow_y = item.rect.centery - self._arrow_image.get_height() // 2
                self.screen.blit(self._arrow_image, (arrow_x, arrow_y))

            # 选中项下方光条
            if i == self.selected_index:
                bar_width = item.rect.width + 40
                bar_height = 3
                bar_rect = pygame.Rect(0, 0, bar_width, bar_height)
                bar_rect.centerx = item.rect.centerx
                bar_rect.top = item.rect.bottom + 6
                alpha = int(128 + 127 * abs(math.sin(item.hover_timer * 2.0)))
                color = (255, 255, 100, alpha)
                bar_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
                bar_surf.fill(color)
                self.screen.blit(bar_surf, bar_rect)

            # 菜单文字
            self.screen.blit(item.image, item.rect)

    def _draw_high_score(self):
        """在标题和菜单项之间显示历史最高分。"""
        high = self.stats.high_score
        if high > 0:
            text = f"HIGH SCORE: {high:,}"
        else:
            text = ""

        if text:
            img = self.info_font.render(text, True, (150, 150, 200))
            rect = img.get_rect(
                centerx=self.screen_rect.centerx,
                top=self.title_base_y + 55)
            self.screen.blit(img, rect)

        # 如果刚从游戏中返回，显示上一局的得分
        if self.stats.score > 0 and not self.stats.game_active:
            last = f"LAST SCORE: {self.stats.score:,}"
            last_img = self.info_font.render(last, True, (200, 200, 150))
            last_rect = last_img.get_rect(
                centerx=self.screen_rect.centerx,
                top=self.title_base_y + 80)
            self.screen.blit(last_img, last_rect)

    def _draw_footer(self):
        """绘制底部提示信息。"""
        lines = [
            u"↑↓ / Mouse — Navigate    ↵ / Click — Select    ESC — Quit",
        ]
        y = self.screen_rect.bottom - 50
        for line in lines:
            img = self.credits_font.render(line, True, (100, 100, 130))
            rect = img.get_rect(centerx=self.screen_rect.centerx, bottom=y)
            self.screen.blit(img, rect)
            y -= 20
