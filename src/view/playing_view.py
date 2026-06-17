from __future__ import annotations
from typing import Optional, Tuple
import pygame as PYG
import os

from src.view.View import View
from src.Config import Colors, SCREEN_SIZE, SCREEN_ZOOM, CONTENT_DIR
from src.utils.resource_loader import load_tileset

class PlayingView(View):
    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.internal_size = (SCREEN_SIZE.WIDTH / SCREEN_ZOOM[1], SCREEN_SIZE.HEIGHT / SCREEN_ZOOM[1])
        self.internal_surf = PYG.Surface(self.internal_size)
        self.current_map_name = ""
        self.map_visual_surface = None
        self.entities_cache = {}
        self.flash_cache = {}
        self._init_ui_assets()
        self._init_player_animations()
        self._init_enemy_animations()
        self.ui_font = PYG.font.SysFont("Courier New", 12, bold=True)

    def _init_ui_assets(self):
        ui_image_path = os.path.join(CONTENT_DIR, "interfaces", "heart", "heart_spreedsheet.png")
        try:
            self.heart_sheet = PYG.image.load(ui_image_path).convert_alpha()
            self.heart_full = self.heart_sheet.subsurface(PYG.Rect(0, 0, 32, 32))
            self.heart_empty = self.heart_sheet.subsurface(PYG.Rect(32, 0, 32, 32))
        except FileNotFoundError:
            print("[UI] Aviso: Imagem dos corações não encontrada.. Usando blocos genéricos.")
            self.heart_full = PYG.Surface((32, 32));  self.heart_full.fill((255, 0, 0))
            self.heart_empty = PYG.Surface((32, 32)); self.heart_empty.fill((50, 50, 50))
        self.heart_scale_size = None
        self.heart_full_scaled = None
        self.heart_empty_scaled = None

    def _init_player_animations(self):
        idle_sheet_path = os.path.join(CONTENT_DIR, "player", "images", "player.png")
        self.idle_sheet = PYG.image.load(idle_sheet_path).convert_alpha()
        self.idle_frames = {
            "up":    self.idle_sheet.subsurface(PYG.Rect(32,  0, 32, 32)),
            "left":  self.idle_sheet.subsurface(PYG.Rect(0,  32, 32, 32)),
            "down":  self.idle_sheet.subsurface(PYG.Rect(32, 32, 32, 32)),
            "right": self.idle_sheet.subsurface(PYG.Rect(64, 32, 32, 32))
        }
        self.run_animations = {}
        for d in ["up", "down", "left", "right"]:
            gif_path = os.path.join(CONTENT_DIR, "player", "animations", "walk", f"player_walk_{d}.gif")
            if os.path.exists(gif_path): self.run_animations[d] = list(PYG.image.load_animation(gif_path))
            else: self.run_animations[d] = [self.idle_frames[d]]
        self.anim_index = 0
        self.anim_timer = 0.0
        self.frame_duration = 0.12

    def _init_enemy_animations(self):
        self.enemy_anim_states = {}
        self.enemy_frame_duration = 0.12
        self.enemy_anims = { "idle": [], "walk": [], "attack": [], "death": [] }
        enemy_dir = os.path.join(CONTENT_DIR, "enemy", "animations")
        for state in ["idle", "walk", "attack", "death"]:
            path = os.path.join(enemy_dir, state, f"enemy_{state}.gif")
            if os.path.exists(path):
                self.enemy_anims[state] = list(PYG.image.load_animation(path))

    def update(self, delta_time: float, player_model, enemies):
        if not player_model.is_moving:
            self.anim_index, self.anim_timer = 0, 0.0
        else:
            self.anim_timer += delta_time
            if self.anim_timer >= self.frame_duration:
                self.anim_timer = 0.0
                current_anim_list = self.run_animations[player_model.direction]
                self.anim_index = (self.anim_index + 1) % len(current_anim_list)
        active_enemy_ids = {id(enemy) for enemy in enemies}
        keys_to_remove = [e_id for e_id in self.enemy_anim_states if e_id not in active_enemy_ids]
        for e_id in keys_to_remove: 
            del self.enemy_anim_states[e_id]
        for enemy in enemies:
            enemy_id = id(enemy)
            if enemy_id not in self.enemy_anim_states:
                self.enemy_anim_states[enemy_id] = {"index": 0, "timer": 0.0, "state": enemy.state}
            state_data = self.enemy_anim_states[enemy_id]
            if state_data["state"] != enemy.state:
                state_data.update({"index": 0, "timer": 0.0, "state": enemy.state})
            state_data["timer"] += delta_time
            if state_data["timer"] >= self.enemy_frame_duration:
                state_data["timer"] = 0.0
                anim_list = self.enemy_anims.get(enemy.state, [])
                if anim_list:
                    if enemy.state == "death":
                        if state_data["index"] < len(anim_list) - 1: state_data["index"] += 1
                        else: enemy.ready_to_remove = True
                    else: state_data["index"] = (state_data["index"] + 1) % len(anim_list)

    def draw(
            self, 
            player_model, 
            map_model, 
            camera, 
            enemies, 
            projectiles, 
            npcs, 
            near_cutscene_pos: Optional[Tuple[int, int]] = None
        ):
        self.internal_surf.fill(Colors.BG)
        offset_x, offset_y = int(camera.x), int(camera.y)
        self._draw_map(map_model, offset_x, offset_y)
        self._draw_player(player_model, offset_x, offset_y)
        self._draw_projectiles(projectiles, offset_x, offset_y)
        self._draw_entities(map_model, offset_x, offset_y)
        self._draw_enemies(enemies, offset_x, offset_y)
        self._draw_npcs(npcs, offset_x, offset_y)
        if near_cutscene_pos: self._draw_cutscene_prompt(near_cutscene_pos, offset_x, offset_y)
        PYG.transform.scale(self.internal_surf, self.screen.get_size(), self.screen)
        self._draw_ui(player_model, map_model.tile_size)

    def _draw_map(self, map_model, offset_x, offset_y):
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
                print(f"[View] Erro: Arte final '{map_model.visual_image_path}' não encontrada.")
                self.map_visual_surface = PYG.Surface((800, 600))
                self.map_visual_surface.fill((255, 0, 255))
            self.entities_cache = load_tileset(map_model.entities_tileset, tile_size)
            self.current_map_name = map_model.map_name
        if self.map_visual_surface:
            self.internal_surf.blit(self.map_visual_surface, (-offset_x, -offset_y))

    def _draw_player(self, player_model, offset_x, offset_y):
        render_player = True
        if player_model.invulnerable_timer > 0 and int(player_model.invulnerable_timer * 10) % 2 == 0:
            render_player = False
        if render_player:
            current_frame = self.run_animations[player_model.direction][self.anim_index][0] if player_model.is_moving else self.idle_frames[player_model.direction]
            px, py = player_model.rect.x - offset_x, player_model.rect.y - offset_y
            if player_model.direction == "up":
                self.internal_surf.blit(current_frame, (px, py))
                self._draw_tail(player_model, offset_x, offset_y)
            else:
                self._draw_tail(player_model, offset_x, offset_y)
                self.internal_surf.blit(current_frame, (px, py))

    def _draw_tail(self, player_model, offset_x, offset_y):
        radius_func = lambda i: max(1, int(5.5 - i * 0.5))
        for i, point in enumerate(player_model.tail_points):
            base_radius = radius_func(i)
            tx, ty = int(point[0] - offset_x), int(point[1] - offset_y)
            current_outline = Colors.FOX_PURPLE if i >= player_model.num_tail_segments - 3 else Colors.FOX_OUTLINE
            PYG.draw.circle(self.internal_surf, current_outline, (tx, ty), base_radius + 2)
        for i, point in enumerate(player_model.tail_points):
            base_radius = radius_func(i)
            tx, ty = int(point[0] - offset_x), int(point[1] - offset_y)
            current_color = Colors.FOX_TIP if i >= player_model.num_tail_segments - 3 else Colors.FOX_BASE
            PYG.draw.circle(self.internal_surf, current_color, (tx, ty), base_radius)

    def _draw_projectiles(self, projectiles, offset_x, offset_y):
        for proj in projectiles:
            tx, ty = int(proj.x - offset_x), int(proj.y - offset_y)
            PYG.draw.circle(self.internal_surf, (214, 200, 252), (tx, ty), 6)
            PYG.draw.circle(self.internal_surf, (179, 102, 246), (tx, ty), 8, 2)

    def _draw_entities(self, map_model, offset_x, offset_y):
        for entity_name, grid_x, grid_y in map_model.overhead_entities:
            x = grid_x * map_model.tile_size - offset_x
            y = grid_y * map_model.tile_size - offset_y
            if -map_model.tile_size < x < self.internal_size[0] and -map_model.tile_size < y < self.internal_size[1]:
                img_entity = self.entities_cache.get(entity_name)
                if img_entity: 
                    self.internal_surf.blit(img_entity, (x, y))

    def _draw_enemies(self, enemies, offset_x, offset_y):
        for enemy in enemies:
            ex, ey = enemy.rect.x - offset_x, enemy.rect.y - offset_y
            if -32 < ex < self.internal_size[0] and -32 < ey < self.internal_size[1]:
                state_data = self.enemy_anim_states.get(id(enemy))
                frame_idx = state_data["index"] if state_data else 0
                anim_list = self.enemy_anims.get(enemy.state, [])
                if anim_list and frame_idx < len(anim_list):
                    enemy_frame = anim_list[frame_idx][0]
                    if getattr(enemy, "hit_timer", 0) > 0:
                        frame_id = id(enemy_frame)
                        if frame_id not in self.flash_cache:
                            flash_frame = enemy_frame.copy()
                            flash_frame.fill((255, 50, 50, 255), special_flags=PYG.BLEND_RGB_MULT)
                            self.flash_cache[frame_id] = flash_frame
                        self.internal_surf.blit(self.flash_cache[frame_id], (ex, ey))
                    else:
                        self.internal_surf.blit(enemy_frame, (ex, ey))
                else:
                    PYG.draw.rect(
                        self.internal_surf,
                        (200, 0, 0),
                        (ex, ey, 32, 32)
                    )

    def _draw_npcs(self, npcs, offset_x, offset_y):
        for npc in npcs:
            nx, ny = npc.rect.x - offset_x, npc.rect.y - offset_y
            if -32 < nx < self.internal_size[0] and -32 < ny < self.internal_size[1]:
                if npc.is_interacting: 
                    PYG.draw.rect(
                        self.internal_surf,
                        (255, 255, 255),
                        (nx - 10, ny - 20, 50, 15),
                        border_radius=5
                    )

    def _draw_cutscene_prompt(self, near_pos: Tuple[int, int], offset_x: int, offset_y: int):
        screen_x = near_pos[0] - offset_x + 16
        screen_y = near_pos[1] - offset_y - 15
        text_surf = self.ui_font.render("[E] Salvá-lo", True, (0, 0, 0))
        bg_rect = text_surf.get_rect(center=(screen_x, screen_y))
        bg_rect.inflate_ip(12, 8)
        PYG.draw.rect(self.internal_surf, (255, 255, 255), bg_rect, border_radius=4)
        PYG.draw.rect(self.internal_surf, (0, 0, 0), bg_rect, width=1, border_radius=4)
        self.internal_surf.blit(text_surf, text_surf.get_rect(center=(screen_x, screen_y)))

    def _draw_ui(self, player_model, tile_size):
        ui_start_x, ui_start_y = 20, 20
        scale_heart = tile_size * 4
        if self.heart_scale_size != scale_heart:
            self.heart_scale_size = scale_heart
            size_heart = (scale_heart, scale_heart)
            self.heart_full_scaled = PYG.transform.scale(self.heart_full, size_heart)
            self.heart_empty_scaled = PYG.transform.scale(self.heart_empty, size_heart)
        spacing = scale_heart + 2
        for i in range(player_model.max_health):
            heart_x = ui_start_x + (i * spacing)
            if i < player_model.current_health:
                self.screen.blit(self.heart_full_scaled, (heart_x, ui_start_y))
            else:
                self.screen.blit(self.heart_empty_scaled, (heart_x, ui_start_y))
