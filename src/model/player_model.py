
import pygame as PYG

from src.utils.math_utils import normalize_vector

class PlayerModel:
    def __init__(self, x: float, y: float, size: int = 32):
        self.rect = PYG.Rect(int(x), int(y), size, size)
        
        self.hitbox = PYG.Rect(0, 0, 20, 16)
        self.hitbox.midbottom = self.rect.midbottom
        
        self.pos_x = float(self.hitbox.centerx)
        self.pos_y = float(self.hitbox.centery)
        self.speed = 150.0
    
    def move(self, dx: float, dy: float, delta_time: float, map_model: MapModel):
        norm_dx, norm_dy = normalize_vector(dx, dy)
        
        self.pos_x += norm_dx * self.speed * delta_time
        self.hitbox.centerx = int(self.pos_x)
        if self._check_collision(map_model):
            self.pos_x -= norm_dx * self.speed * delta_time
            self.hitbox.centerx = int(self.pos_x)
        
        self.pos_y += norm_dy * self.speed * delta_time
        self.hitbox.centery = int(self.pos_y)
        if self._check_collision(map_model):
            self.pos_y -= norm_dy * self.speed * delta_time
            self.hitbox.centery = int(self.pos_y)
        
        self.rect.midbottom = self.hitbox.midbottom

    def _check_collision(self, map_model: MapModel) -> bool:
        corners = [
            self.hitbox.topleft, self.hitbox.topright,
            self.hitbox.bottomleft, self.hitbox.bottomright
        ]
        for cx, cy in corners:
            grid_x = int(cx // map_model.tile_size)
            grid_y = int(cy // map_model.tile_size)
            if map_model.is_wall(grid_x, grid_y): return True
        return False
