import pygame

class Ship: #管理飞船的类
    def __init__(self, ai_game): #初始化飞船并设置其初始位置
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        self.image = pygame.image.load('images/ship.png') #加载飞船图像
        self.rect = self.image.get_rect() #获取其外接矩形

        self.rect.midbottom = self.screen_rect.midbottom #对于每艘新飞船，都将其放在屏幕底部的中央

        self.x = float(self.rect.x) #在飞船属性x中存储最小值

        self.moving_right = False #移动标志
        self.moving_left = False

    def update(self): #根据移动标志调整飞船的位置
        if self.moving_right and self.rect.right < self.screen_rect.right: #更新飞船而不是rect对象的x值
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        self.rect.x = self.x #根据self.x更新rect对象

    def blitme(self): #在指定位置绘制飞船
        self.screen.blit(self.image, self.rect)