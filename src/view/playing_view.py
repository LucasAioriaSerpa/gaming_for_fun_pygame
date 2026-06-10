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
        self.current_map_name = ""
        self.map_visual_surface = None
        self.entities_cache = {}
        ui_image_path = os.path.join(CONTENT_DIR, "interfaces", "heart/heart_spreedsheet.png")
        try:
            self.heart_sheet = PYG.image.load(ui_image_path).convert_alpha()
            self.heart_full = self.heart_sheet.subsurface(PYG.Rect(0,0,32,32))
            self.heart_empty = self.heart_sheet.subsurface(PYG.Rect(32,0,32,32))
        except FileNotFoundError:
            print("[UI] Aviso: Imagem dos corações não encontrada.. Usando blocos genéricos.")
            self.heart_full = PYG.Surface((32,32))
            self.heart_full.fill((255,0,0))
            self.heart_empty = PYG.Surface((32,32))
            self.heart_empty.fill((50,50,50))
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
        offset_x = int(camera.x)
        offset_y = int(camera.y)
        tile_size = map_model.tile_size
        if self.current_map_name != map_model.map_name:
            full_path = os.path.join(CONTENT_DIR, "maps", map_model.visual_image_path)
            try:
                self.map_visual_surface = PYG.image.load(full_path).convert_alpha()
                target_width  = map_model.width_tiles  * tile_size
                target_height = map_model.height_tiles * tile_size
                if self.map_visual_surface.get_size() != (target_width, target_height):
                    self.map_visual_surface = PYG.transform.scale(self.map_visual_surface, (target_width, target_height))
            except FileNotFoundError:
                print(f"[View] Erro: Arte final do map '{map_model.visual_image_path}' não encontrada.")
                self.map_visual_surface = PYG.Surface((800, 600))
                self.map_visual_surface.fill((255, 0, 255))
            self.entities_cache = load_tileset(map_model.entities_tileset, tile_size)
            self.current_map_name = map_model.map_name
        if self.map_visual_surface:
            self.internal_surf.blit(self.map_visual_surface, (-offset_x, -offset_y))
        #? Camada 3: Personagem (Z-index da Cauda de maneira dinamica)
        if player_model.is_moving:
            current_frame = self.run_animations[player_model.direction][self.anim_index][0]
        else: 
            current_frame = self.idle_frames[player_model.direction]
        px = player_model.rect.x - offset_x
        py = player_model.rect.y - offset_y
        if player_model.direction == "up":
            self.internal_surf.blit(current_frame, (px, py))
            self._draw_tail(player_model, offset_x, offset_y)
        else:
            self._draw_tail(player_model, offset_x, offset_y)
            self.internal_surf.blit(current_frame, (px, py))
        for entity_name, grid_x, grid_y in map_model.overhead_entities:
            x = grid_x * tile_size - offset_x
            y = grid_y * tile_size - offset_y
            if -tile_size < x < self.internal_size[0] and -tile_size < y < self.internal_size[1]:
                img_entity = self.entities_cache.get(entity_name)
                if img_entity: self.internal_surf.blit(img_entity, (x,y))
        PYG.transform.scale(self.internal_surf, self.screen.get_size(), self.screen)
        ui_start_x = 20
        ui_start_y = 20
        scale_heart = tile_size * 4
        size_heart = (scale_heart, scale_heart)
        spacing = scale_heart + 2
        for i in range(player_model.max_health):
            heart_x = ui_start_x + (i * spacing)
            if i < player_model.current_health:
                self.screen.blit(PYG.transform.scale(self.heart_full, size_heart), (heart_x, ui_start_y))
            else:
                self.screen.blit(PYG.transform.scale(self.heart_empty, size_heart), (heart_x, ui_start_y))

    def _draw_tail(self, player_model: PlayerModel, offset_x: int, offset_y: int):
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

    def player_model_to_screen(self, player_model: PlayerModel) -> tuple[int, int]:
        return (int(player_model.rect.x), int(player_model.rect.y))
