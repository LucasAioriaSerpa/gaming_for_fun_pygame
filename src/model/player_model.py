
import pygame as PYG
import math

from src.utils.math_utils import normalize_vector

class PlayerModel:
    def __init__(self, x: float, y: float, size: int = 32):
        self.rect = PYG.Rect(int(x), int(y), size, size)
        self.hitbox = PYG.Rect(0, 0, 20, 16)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos_x = float(self.hitbox.centerx)
        self.pos_y = float(self.hitbox.centery)
        self.speed = 150.0
        self.direction = "down"
        self.is_moving = False
        self.num_tail_segments = 6
        self.tail_segments_length = 5
        self.tail_points = [[self.pos_x, self.pos_y] for _ in range(self.num_tail_segments)]
    
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
        self._update_tail_physics()

    def _update_tail_physics(self):
        self.tail_points[0][0] = float(self.hitbox.centerx)
        self.tail_points[0][1] = float(self.hitbox.bottom - 4)
        for i in range(1, self.num_tail_segments):
            prev = self.tail_points[i - 1]
            curr = self.tail_points[i]
            dx = prev[0] - curr[0]
            dy = prev[1] - curr[1]
            distance = math.hypot(dx, dy)
            if distance > self.tail_segments_length:
                target_dist = distance - self.tail_segments_length
                curr[0] += (dx / distance * target_dist)
                curr[1] += (dy / distance * target_dist)

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
