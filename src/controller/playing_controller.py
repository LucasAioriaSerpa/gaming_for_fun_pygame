
from __future__ import annotations
from typing import Callable, List
import pygame as PYG

from src.core.Controller import Controller
from src.model.player_model import PlayerModel
from src.model.map_model import MapModel
from src.view.playing_view import PlayingView
from src.utils.camera import Camera
from src.Config import GameState

class PlayingController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        super().__init__(screen, change_state_cb)
        self.view = PlayingView(screen)
        self.camera = Camera(self.view.internal_size[0], self.view.internal_size[1])
        self.load_map("maps/map_01")
    
    def load_map(self, map_name: str):
        self.map_model = MapModel(map_name=map_name, tile_size=32)
        self.player_model = PlayerModel(
            x=self.map_model.spawn_x,
            y=self.map_model.spawn_y,
            size=32
        )        
        self.camera.x = self.player_model.rect.centerx - (self.camera.width / 2)
        self.camera.y = self.player_model.rect.centery - (self.camera.height / 2)
    
    def handle_events(self, events: List[PYG.event.Event]):
        for event in events:
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
        center_x = self.player_model.hitbox.centerx
        center_y = self.player_model.hitbox.centery
        current_tile = self.map_model.get_tile_at(center_x, center_y)
        if current_tile in self.map_model.transitions:
            next_map_filename = self.map_model.transitions[current_tile]
            self.load_map(next_map_filename)
            return
        self.camera.follow(center_x, center_y)
        self.view.update(delta_time, self.player_model)
    
    def draw(self): self.view.draw(self.player_model, self.map_model, self.camera)
