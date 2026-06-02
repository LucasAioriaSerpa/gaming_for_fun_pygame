
from __future__ import annotations

from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import os

from src.view.View import View
from src.Config import Colors, SCREEN_SIZE, SCREEN_ZOOM, IMAGES_DIR
from src.utils.resource_loader import load_tile

class PlayingView(View):

    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.internal_size = (SCREEN_SIZE.WIDTH/SCREEN_ZOOM[1], SCREEN_SIZE.HEIGHT/SCREEN_ZOOM[1])
        self.internal_surf = PYG.Surface(self.internal_size)
        self.floor_img  = load_tile("tiles_sets/floor.png",  (32, 32))
        self.wall_img   = load_tile("tiles_sets/wall.png",   (32, 32))
        self.door_img   = load_tile("tiles_sets/door.png",   (32, 32))
        idle_sheet_path = os.path.join(IMAGES_DIR, "player", "player.png")
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
            gif_path = os.path.join(IMAGES_DIR, "player", f"player_walk_{d}.gif")
            if os.path.exists(gif_path):
                self.run_animations[d] = list(PYG.image.load_animation(gif_path))
            else: self.run_animations[d] = [self.idle_frames[d]]
        self.anim_index = 0
        self.anim_timer = 0.0
        self.frame_duration = 0.12

    def update(self, delta_time: float, player_model: PlayerModel):
        if not player_model.is_moving:
            self.anim_index = 0
            self._anim_timer = 0.0
        else:
            self.anim_timer += delta_time
            if self.anim_timer >= self.frame_duration:
                self.anim_timer = 0.0
                current_anim_list = self.run_animations[player_model.direction]
                self.anim_index = (self.anim_index + 1) % len(current_anim_list)

    def draw(self, player_model: PlayerModel, map_model: MapModel, camera: Camera):
        self.internal_surf.fill(Colors.BG)
        offset_x = int(camera.x)
        offset_y = int(camera.y)
        self._draw_tiles(offset_x, offset_y, map_model)
        self._draw_tail(offset_x, offset_y, player_model)
        if player_model.is_moving:
            current_frame = self.run_animations[player_model.direction][self.anim_index][0]
        else: current_frame = self.idle_frames[player_model.direction]
        px = player_model.rect.x - offset_x
        py = player_model.rect.y - offset_y
        self.internal_surf.blit(current_frame, (px, py))
        PYG.transform.scale(self.internal_surf, self.screen.get_size(), self.screen)
    
    def _draw_tiles(self, offset_x: int, offset_y: int, map_model: MapModel):
        for row_idx, row in enumerate(map_model.grid):
            for col_idx, tile_type in enumerate(row):
                x = col_idx * map_model.tile_size - offset_x
                y = row_idx * map_model.tile_size - offset_y
                if -32 < x < self.internal_size[0]  and -32 < y < self.internal_size[1]:
                    match tile_type:
                        case "X": self.internal_surf.blit(self.wall_img,  (x, y))
                        case ".": self.internal_surf.blit(self.floor_img, (x, y))
                        case "E":
                            self.internal_surf.blit(self.floor_img, (x, y))
                            self.internal_surf.blit(self.door_img, (x, y))
    
    def _draw_tail(self, offset_x: int, offset_y: int, player_model: PlayerModel):
        COLOR_BASE      = (250, 151, 109)
        COLOR_TIP       = (214, 200, 252)
        COLOR_OUTLINE   = (101,   6,  14)
        #? outline
        for i, point in enumerate(player_model.tail_points):
            base_radius = max(0, int(6.5 - i * 0.6)) #* default 6.5 - i * 0.6
            outline_radius = base_radius + 2
            tx = int(point[0] - offset_x)
            ty = int(point[1] - offset_y)
            PYG.draw.circle(self.internal_surf, COLOR_OUTLINE, (tx, ty), outline_radius)
        #? outline
        for i, point in enumerate(player_model.tail_points):
            base_radius = max(1, int(6.5 - i * 0.6))
            print(base_radius)
            tx = int(point[0] - offset_x)
            ty = int(point[1] - offset_y)
            if i >= player_model.num_tail_segments - 3:
                current_color = COLOR_TIP
            else:
                current_color = COLOR_BASE
            PYG.draw.circle(self.internal_surf, current_color, (tx, ty), base_radius)
    
    def player_model_to_screen(self, player_model: PlayerModel) -> tuple[int, int]:
        return (int(player_model.rect.x), int(player_model.rect.y))
