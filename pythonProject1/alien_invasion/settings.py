class Settings: #存储游戏中所有设置的类
    def __init__(self): #初始化游戏的设置
        self.screen_width = 1200 #屏幕设置
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        self.ship_speed = 1.5 #飞船设置

        self.bullet_speed = 1.0 #子弹设置
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # 外星人设置
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10 #有外星人撞到屏幕边缘时外星人群下移速度
        self.fleet_direction = 1 #1表示右移，-1表示左移