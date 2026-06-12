
from __future__ import annotations
from typing import Callable, List
import pygame as PYG
import math

from src.Config import GameState, SCREEN_ZOOM
from src.core.Controller import Controller
from src.view.playing_view import PlayingView
from src.model.player_model import PlayerModel
from src.model.enemy_model import EnemyModel
from src.model.npc_model import NPCModel
from src.model.projectile_mode import ProjectileModel
from src.model.map_model import MapModel
from src.utils.math_utils import normalize_vector
from src.utils.camera import Camera

class PlayingController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        super().__init__(screen, change_state_cb)
        self.view = PlayingView(screen)
        self.camera = Camera(self.view.internal_size[0], self.view.internal_size[1])
        self.enemies: List[EnemyModel] = []
        self.npcs: List[NPCModel] = []
        self.projectiles: List[ProjectileModel] = []
        self.load_map("maps/map_01")
    
    def on_enter(self): self.__init__(self.screen, self.change_state)
    
    def trigger_game_over(self): self.change_state(GameState.GAME_OVER)
    
    def load_map(self, map_name: str):
        self.projectiles.clear()
        self.map_model = MapModel(map_name=map_name, tile_size=32)
        self.player_model = PlayerModel(
            x=self.map_model.spawn_x,
            y=self.map_model.spawn_y,
            size=32
        )
        self.enemies.clear()
        for ex, ey in self.map_model.enemy_spawns:
            self.enemies.append(EnemyModel(x=ex * 32, y=ey * 32, size=32))
        self.npcs.clear()
        for nx, ny in self.map_model.npc_spawns:
            self.npcs.append(NPCModel(x=nx * 32, y=ny * 32, size=32))
        self.camera.x = self.player_model.rect.centerx - (self.camera.width / 2)
        self.camera.y = self.player_model.rect.centery - (self.camera.height / 2)
    
    def handle_events(self, events: List[PYG.event.Event]):
        for event in events:
            match event.type:
                case PYG.KEYDOWN:
                    match event.key:
                        case PYG.K_ESCAPE:
                            self.change_state(GameState.START_SCREEN)
                        case PYG.K_e:
                            for npc in self.npcs:
                                dx = self.player_model.hitbox.centerx - npc.hitbox.centerx
                                dy = self.player_model.hitbox.centery - npc.hitbox.centery
                                distance = math.hypot(dx, dy)
                                if distance <= 50.0:
                                    npc.interact()
                                    break
            if event.type == PYG.KEYDOWN and event.key == PYG.K_ESCAPE:
                self.change_state(GameState.START_SCREEN)
            

    def update(self, delta_time: float): 
        keys = PYG.key.get_pressed()
        dx, dy = 0.0,  0.0
        if keys[PYG.K_w] or keys[PYG.K_UP]:     dy -= 1.0
        if keys[PYG.K_s] or keys[PYG.K_DOWN]:   dy += 1.0
        if keys[PYG.K_a] or keys[PYG.K_LEFT]:   dx -= 1.0
        if keys[PYG.K_d] or keys[PYG.K_RIGHT]:  dx += 1.0
        if dx != 0.0 or dy != 0.0:
            self.player_model.is_moving = True
            if abs(dx) >= abs(dy):
                self.player_model.direction = "right" if dx > 0 else "left"
            else:
                self.player_model.direction = "down" if dy > 0 else "up"
        else: self.player_model.is_moving = False
        self.player_model.move(dx, dy, delta_time, self.map_model)
        self.player_model.update_timers(delta_time)
        if PYG.mouse.get_pressed()[0]:
            if self.player_model.attack_timer <= 0:
                mx, my = PYG.mouse.get_pos()
                world_x = (mx / SCREEN_ZOOM[1]) + self.camera.x
                world_y = (my / SCREEN_ZOOM[1]) + self.camera.y
                dir_x = world_x - self.player_model.hitbox.centerx
                dir_y = world_y - self.player_model.hitbox.centery
                norm_dx, norm_dy = normalize_vector(dir_x, dir_y)
                if norm_dx != 0 or norm_dy != 0:
                    new_proj = ProjectileModel(
                        self.player_model.hitbox.centerx,
                        self.player_model.hitbox.centery,
                        norm_dx, norm_dy
                    )
                    self.projectiles.append(new_proj)
                    self.player_model.attack_timer = self.player_model.attack_cooldown
        if hasattr(self.player_model, "current_health") and self.player_model.current_health <= 0: 
            self.trigger_game_over()
        for proj in self.projectiles:
            proj.update(delta_time)
            grid_x, grid_y = int(proj.x // 32), int(proj.y // 32)
            if self.map_model.is_wall(grid_x, grid_y):
                proj.active = False
                continue
            for enemy in self.enemies:
                if enemy.state != "death" and proj.hitbox.colliderect(enemy.hitbox):
                    enemy.take_damage(
                        amount=1,
                        dir_x=proj.dir_x,
                        dir_y=proj.dir_y,
                        force=0.5,
                        map_model=self.map_model
                    )
                    proj.active = False
                    break
        self.projectiles = [p for p in self.projectiles if p.active]
        center_x = self.player_model.hitbox.centerx
        center_y = self.player_model.hitbox.centery
        current_tile = self.map_model.get_tile_at(center_x, center_y)
        if current_tile in self.map_model.transitions:
            next_map_filename = self.map_model.transitions[current_tile]
            self.load_map(next_map_filename)
            return
        self.camera.follow(center_x, center_y)
        for enemy in self.enemies:
            enemy.update(delta_time, self.player_model, self.map_model)
        self.enemies = [e for e in self.enemies if not e.ready_to_remove]
        self.view.update(delta_time, self.player_model, self.enemies)

    def draw(self): self.view.draw(self.player_model, self.map_model, self.camera, self.enemies, self.projectiles, self.npcs)
