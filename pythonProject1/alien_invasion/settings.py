class Settings:  # 存储游戏中所有设置的类
    def __init__(self):  # 初始化游戏的设置
        # ── 屏幕设置 ─────────────────────────────────────
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (10, 10, 30)  # 深空背景色（配合星空）
        self.fps = 60  # 帧率限制

        # ── 音效设置 ─────────────────────────────────────
        self.sound_enabled = True

        # ── 飞船设置 ─────────────────────────────────────
        self.ship_speed = 6.0
        self.ship_limit = 3

        # ── 子弹设置 ─────────────────────────────────────
        self.bullet_speed = 7.0
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (255, 255, 100)  # 明亮黄色，在深色背景中更可见
        self.bullets_allowed = 7

        # ── 外星人设置 ──────────────────────────────────
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10  # 外星人撞到屏幕边缘时下移速度
        self.fleet_direction = 1  # 1=右移，-1=左移

        # 难度递增系数
        self.speedup_scale = 1.1     # 每轮速度增长
        self.score_scale = 1.5       # 每轮分数增长

        # 残血加速：剩余外星人越少，速度越快
        self.fleet_ramp_enabled = True
        self.fleet_ramp_max_multiplier = 2.5  # 最后几个外星人速度最高×2.5

        # ── 精英外星人设置 ──────────────────────────────
        # 从第3波开始，部分外星人升级为精英（双倍分数，1.3倍速度）
        self.elite_alien_chance = 0.0       # 基础概率
        self.elite_alien_chance_per_level = 0.08  # 每级+8%
        self.elite_alien_max_chance = 0.40  # 最多40%
        self.elite_points_multiplier = 2    # 精英分数倍率
        self.elite_speed_multiplier = 1.3   # 精英速度倍率

        # ── Boss外星人设置 ──────────────────────────────
        # 从第5波开始，每波出现1个Boss（3倍分数，需2击中才死，发射慢速子弹）
        self.boss_alien_level_start = 5
        self.boss_health = 2                # 需要多少发子弹才能击毁
        self.boss_points_multiplier = 5     # Boss分数倍率
        self.boss_size_scale = 1.8          # Boss比普通外星人大多少

        # ── 道具设置 ────────────────────────────────────
        self.powerup_drop_chance = 0.12     # 击杀外星人掉落道具概率
        self.powerup_fall_speed = 2.0       # 道具下落速度
        self.powerup_rapid_fire_duration = 8.0   # 速射道具持续时间（秒）
        self.powerup_shield_duration = 7.0       # 护盾持续时间（秒）
        self.powerup_spread_shot_duration = 10.0  # 散射持续时间（秒）

        # ── 连击设置 ────────────────────────────────────
        self.combo_timeout = 1.2  # 连续击杀间隔超过此秒数则重置连击
        self.combo_score_bonus_per_level = 10  # 每次连击额外加分 = combo_level × 此值

        # ── 屏幕震动设置 ───────────────────────────────
        self.screen_shake_duration = 12  # 震动持续帧数
        self.screen_shake_intensity = 6  # 最大偏移像素

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):  # 初始化随游戏进行而变化的设置
        self.ship_speed = 6.0
        self.bullet_speed = 7.0
        self.alien_speed = 1.0

        self.fleet_direction = 1  # 1=向右，-1=向左

        # 计分
        self.alien_points = 50

    def increase_speed(self):  # 提高速度设置和外星人分数
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
