import json
import os


class GameStats: #跟踪游戏的统计信息
    def __init__(self, ai_game): #初始化统计信息
        self.settings = ai_game.settings
        self.reset_stats()
        # 游戏刚启动时处于非活动状态
        self.game_active = False
        # 游戏暂停标志
        self.game_paused = False
        # 本会话已游玩局数（用于主菜单文本切换）
        self.games_played = 0
        # 从文件加载最高分（任何情况下都不应重置最高分）
        self.high_score = self._load_high_score()

    def reset_stats(self): #初始化在运行游戏期间可能变化的统计信息
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def _get_high_score_path(self):
        """获取最高分存档文件的路径"""
        return os.path.join(os.path.dirname(__file__), 'high_score.json')

    def _load_high_score(self):
        """从文件加载历史最高分，文件不存在或损坏时返回0"""
        try:
            with open(self._get_high_score_path(), 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        """将最高分持久化到文件"""
        try:
            with open(self._get_high_score_path(), 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except IOError:
            pass  # 写入失败时静默忽略，不影响游戏运行
