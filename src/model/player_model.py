
import pygame as PYG
import math

from src.utils.math_utils import normalize_vector
from src.model.map_model import MapModel

class PlayerModel:
    def __init__(self, x: float, y: float, size: int = 32):
        self.rect = PYG.Rect(int(x), int(y), size, size)
        self.hitbox = PYG.Rect(0, 0, 20, 16)
        self.hitbox.midbottom = self.rect.midbottom
        self.pos_x = float(self.hitbox.centerx)
        self.pos_y = float(self.hitbox.centery)
        self.speed = 100.0
        self.direction = "down"
        self.is_moving = False
        self.max_health = 3
        self.current_health = 3
        self.is_dead = False
        self.invulnerable_timer = 0.0
        self.attack_cooldown = 0.4
        self.attack_timer = 0.0
        self.wag_timer = 0.0
        self.num_tail_segments = 10
        self.tail_segments_length = 2.5
        self.tail_points = [[self.pos_x, self.pos_y] for _ in range(self.num_tail_segments)]
    
    def check_health(self) -> bool:
        if self.current_health <= 0:
            self.current_health = 0
            self.is_dead = True
            return True
        return False
    
    def take_damage(self, amount: int):
        if self.invulnerable_timer <= 0:
            self.current_health -= amount
            self.invulnerable_timer = 1.0
            
    def update_timers(self, delta_time: float):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= delta_time
        if self.attack_timer > 0:
            self.attack_timer -= delta_time
    
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
        self._update_tail_physics(delta_time)

    def _update_tail_physics(self, delta_time: float):
        self.wag_timer += delta_time
        self.tail_points[0][0] = float(self.hitbox.centerx)
        self.tail_points[0][1] = float(self.hitbox.bottom - 10)
        wag_speed = 12.0 if self.is_moving else 3.5
        wag_amount = 60.0 if self.is_moving else 15.0
        bias_x, bias_y = 0.0, 0.0
        match self.direction:
            case "up":
                self.tail_points[0][0] += 0 #* point_X
                self.tail_points[0][1] += 8 #* point_Y
                bias_y =  1.0
            case "down":
                self.tail_points[0][0] -= 0
                self.tail_points[0][1] -= 2
                bias_y = -1.0
            case "left":
                self.tail_points[0][0] += 2
                self.tail_points[0][1] += 2
                bias_x =  1.0
            case "right":
                self.tail_points[0][0] -= 2
                self.tail_points[0][1] += 2
                bias_x = -1.0
        for i in range(1, self.num_tail_segments):
            stiffness = 60.0 * delta_time
            self.tail_points[i][0] += bias_x * stiffness
            self.tail_points[i][1] += bias_y * stiffness
            wave = math.sin(self.wag_timer * wag_speed - i * 0.6) * wag_amount * delta_time
            if self.direction in ["up", "down"]:
                self.tail_points[i][0] += wave
            else:
                self.tail_points[i][1] += wave
            prev = self.tail_points[i - 1]
            curr = self.tail_points[i]
            dx = prev[0] - curr[0]
            dy = prev[1] - curr[1]
            distance = math.hypot(dx, dy)
            if distance > 0:
                difference = distance - self.tail_segments_length
                curr[0] += (dx / distance * difference)
                curr[1] += (dy / distance * difference)

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
