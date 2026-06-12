
import pygame as PYG
import math

from src.utils.math_utils import normalize_vector
from src.model.player_model import PlayerModel
from src.model.map_model import MapModel

class EnemyModel:
    def __init__(self, x: float, y: float, size: int = 32) -> None:
        self.rect = PYG.Rect(int(x), int(y), size, size)
        self.hitbox = PYG.Rect(0, 0, 20, 20)
        self.hitbox.center = self.rect.center
        self.pos_x = float(self.hitbox.centerx)
        self.pos_y = float(self.hitbox.centery)
        self.speed = 60.0
        self.health = 3
        self.state = "idle"
        self.detect_range = 150.0
        self.attack_range = 40.0
        self.attack_cooldown = 1.5
        self.attack_timer = 0.0
        self.ready_to_remove = False
        self.has_dealt_damage = False
        self.hit_timer = 0.0

    def update(self, delta_time: float, player: PlayerModel, map_model: MapModel):
        if self.state == "death": return
        if self.health <= 0:
            self.state = "death"
            return
        if self.attack_timer > 0: 
            self.attack_timer -= delta_time
        if self.hit_timer > 0:
            self.hit_timer -= delta_time
        dx = player.hitbox.centerx - self.hitbox.centerx
        dy = player.hitbox.centery - self.hitbox.centery
        distance = math.hypot(dx, dy)
        if distance <= self.attack_range:
            if self.attack_timer <= 0:
                self.state = "attack"
                self.attack_timer = self.attack_cooldown
                self.has_dealt_damage = False
            if self.state == "attack" and not self.has_dealt_damage:
                time_elapsed = self.attack_cooldown - self.attack_timer
                if time_elapsed >= 0.72:
                    self.has_dealt_damage = True
                    if distance <= self.attack_range + 15:
                        player.take_damage(1)
        elif distance <= self.detect_range:
            if self.state == "attack" and self.attack_timer > self.attack_cooldown - 0.5: 
                pass
            else:
                self.state = "walk"
                self._move(dx, dy, distance, delta_time, map_model)
        else:
            self.state = "idle"

    def _move(self, dx: float, dy: float, distance: float, delta_time: float, map_model: MapModel):
        if distance == 0: return
        norm_dx = dx / distance
        norm_dy = dy / distance
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
        self.rect.center = self.hitbox.center

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
