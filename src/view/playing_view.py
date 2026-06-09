from __future__ import annotations

from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import os

from src.view.View import View
from src.Config import Colors, SCREEN_SIZE, SCREEN_ZOOM, CONTENT_DIR
from src.utils.resource_loader import load_tileset

class PlayingView(View):
    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.internal_size = (SCREEN_SIZE.WIDTH/SCREEN_ZOOM[1], SCREEN_SIZE.HEIGHT/SCREEN_ZOOM[1])
        self.internal_surf = PYG.Surface(self.internal_size)
        self.current_tileset_name = ""
        self.tileset_cache = {}
        idle_sheet_path = os.path.join(CONTENT_DIR, "player", "images/player.png")
        self.idle_sheet = PYG.image.load(idle_sheet_path).convert_alpha()
        self.idle_frames = {
            "up":    self.idle_sheet.subsurface(PYG.Rect(32,  0, 32, 32)),
            "left":  self.idle_sheet.subsurface(PYG.Rect(0,  32, 32, 32)),
            "down":  self.idle_sheet.subsurface(PYG.Rect(32, 32, 32, 32)),
            "right": self.idle_sheet.subsurface(PYG.Rect(64, 32, 32 ,32))
        }
        self.run_animations = {}
        directions = ["up", "down", "left", "right"]
        for d in directions:
            gif_path = os.path.join(CONTENT_DIR, "player", f"animations/walk/player_walk_{d}.gif")
            if os.path.exists(gif_path):
                self.run_animations[d] = list(PYG.image.load_animation(gif_path))
            else: self.run_animations[d] = [self.idle_frames[d]]
        self.anim_index = 0
        self.anim_timer = 0.0
        self.frame_duration = 0.12

    def update(self, delta_time: float, player_model: PlayerModel):
        if not player_model.is_moving:
            self.anim_index = 0
            self.anim_timer = 0.0
        else:
            self.anim_timer += delta_time
            if self.anim_timer >= self.frame_duration:
                self.anim_timer = 0.0
                current_anim_list = self.run_animations[player_model.direction]
                self.anim_index = (self.anim_index + 1) % len(current_anim_list)

    def draw(self, player_model: PlayerModel, map_model: MapModel, camera: Camera):
        self.internal_surf.fill(Colors.FOX_OUTLINE)
        #? Verifica se o mapa alterou o tileset ativo
        if self.current_tileset_name != map_model.tileset_name:
            self.tileset_cache = load_tileset(map_model.tileset_name, map_model.tile_size)
            self.current_tileset_name = map_model.tileset_name
        offset_x = int(camera.x)
        offset_y = int(camera.y)
        ts = map_model.tile_size
        #? Camada 1 & 2: Ground & Decor low sendo renderizado juntos
        for row_idx in range(map_model.height_tiles):
            for col_idx in range(map_model.width_tiles):
                x = col_idx * ts - offset_x
                y = row_idx * ts - offset_y
                if -ts < x < self.internal_size[0] and -ts < y < self.internal_size[1]:
                    #? Ground
                    tile_ground = map_model.ground_layer[row_idx][col_idx]
                    img_ground = self.tileset_cache.get(tile_ground, self.tileset_cache.get("fallback"))
                    if img_ground:
                        self.internal_surf.blit(img_ground, (x, y))
                    #? Decor low
                    if row_idx < len(map_model.decor_low_layer) and col_idx < len(map_model.decor_low_layer[row_idx]):
                        tile_low = map_model.decor_low_layer[row_idx][col_idx]
                        if tile_low != "none":
                            img_low = self.tileset_cache.get(tile_low)
                            if img_low:
                                self.internal_surf.blit(img_low, (x, y))
        #? Render da Cauda
        def _draw_tail():
            radius_func = lambda i: max(1, int(5.5 - i * 0.5))
            for i, point in enumerate(player_model.tail_points):
                base_radius = radius_func(i)
                outline_radius = base_radius + 2
                tx = int(point[0] - offset_x)
                ty = int(point[1] - offset_y)
                current_outline = Colors.FOX_PURPLE if i >= player_model.num_tail_segments - 3 else Colors.FOX_OUTLINE
                PYG.draw.circle(self.internal_surf, current_outline, (tx, ty), outline_radius)
            for i, point in enumerate(player_model.tail_points):
                base_radius = radius_func(i)
                tx = int(point[0] - offset_x)
                ty = int(point[1] - offset_y)
                current_color = Colors.FOX_TIP if i >= player_model.num_tail_segments - 3 else Colors.FOX_BASE
                PYG.draw.circle(self.internal_surf, current_color, (tx, ty), base_radius)
        #? Camada 3: Personagem (Z-index da Cauda de maneira dinamica)
        if player_model.is_moving:
            current_frame = self.run_animations[player_model.direction][self.anim_index][0]
        else: 
            current_frame = self.idle_frames[player_model.direction]
        px = player_model.rect.x - offset_x
        py = player_model.rect.y - offset_y
        if player_model.direction == "up":
            self.internal_surf.blit(current_frame, (px, py))
            _draw_tail()
        else:
            _draw_tail()
            self.internal_surf.blit(current_frame, (px, py))
        #? Camada 4: Decor High
        for row_idx in range(len(map_model.decor_high_layer)):
            for col_idx in range(len(map_model.decor_high_layer[row_idx])):
                tile_high = map_model.decor_high_layer[row_idx][col_idx]
                if tile_high != "none":
                    x = col_idx * ts - offset_x
                    y = row_idx * ts - offset_y
                    if -ts < x < self.internal_size[0] and -ts < y < self.internal_size[1]:
                        img_high = self.tileset_cache.get(tile_high)
                        if img_high:
                            self.internal_surf.blit(img_high, (x, y))
        PYG.transform.scale(self.internal_surf, self.screen.get_size(), self.screen)
    
    def player_model_to_screen(self, player_model: PlayerModel) -> tuple[int, int]:
        return (int(player_model.rect.x), int(player_model.rect.y))
