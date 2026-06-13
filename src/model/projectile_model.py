import pygame as PYG

class ProjectileModel:
    def __init__(self, x: float, y: float, dir_x: float, dir_y: float):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = 5.0
        self.active = True
        self.hitbox = PYG.Rect(int(x), int(y), 12, 12)

    def update(self, delta_time: float):
        self.x += self.dir_x * self.speed * delta_time
        self.y += self.dir_y * self.speed * delta_time
        self.hitbox.center = (int(self.x), int(self.y))
