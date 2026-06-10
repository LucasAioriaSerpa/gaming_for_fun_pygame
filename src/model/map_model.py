import json
import os

import pygame as PYG

from src.Config import DATA_DIR, CONTENT_DIR

class MapModel:
    def __init__(self, map_name: str, tile_size: int = 32):
        self.tile_size = tile_size
        self.map_name = map_name
        self.collision_grid = []
        self.transitions = {}
        self.enemy_spawns = []
        self.item_spawns = []
        self.overhead_entities = []
        self.spawn_x = 0.0
        self.spawn_y = 0.0
        self.width_tiles = 0
        self.height_tiles = 0
        self.visual_image_path = ""
        self.visual_surface = None
        self._load_map_data()
    
    def _load_map_data(self):
        filepath = os.path.join(DATA_DIR, f"{self.map_name}.json")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        meta_image_path = data.get("meta_image")
        self.visual_image_path = data.get("visual_image")
        self.entities_tileset = data.get("entities_tileset", "start_area")
        self.color_to_entity = data.get("color_to_entity", {})
        self.transitions_targets = data.get("transitions", {})
        self._parse_meta_image(meta_image_path)

    def _parse_meta_image(self, meta_filename: str):
        full_path = os.path.join(CONTENT_DIR, "maps", meta_filename)
        try:
            meta_surf = PYG.image.load(full_path).convert_alpha()
            self.width_tiles  = meta_surf.get_width()  // self.tile_size
            self.height_tiles = meta_surf.get_height() // self.tile_size
            if self.width_tiles != 0 or self.height_tiles != 0: scale_up = False
            else:
                self.width_tiles = meta_surf.get_width()
                self.height_tiles = meta_surf.get_height()
                scale_up = True
            self.collision_grid = [[False for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
            for y in range(self.height_tiles):
                for x in range(self.width_tiles):
                    if scale_up:
                        pixel_x = x
                        pixel_y = y
                    else:
                        pixel_x = (x * self.tile_size) + (self.tile_size // 2)
                        pixel_y = (y * self.tile_size) + (self.tile_size // 2)
                    r,g,b, a = meta_surf.get_at((pixel_x,pixel_y))
                    if a == 0: continue
                    color_str = f"{r},{g},{b}"
                    if color_str in self.color_to_entity:
                        entity_name = self.color_to_entity[color_str]
                        self.overhead_entities.append((entity_name, x, y))
                    else:
                        match (r,g,b):
                            case (  0,  0,  0):
                                self.collision_grid[y][x] = True    #? PRETO: Parede
                            case (  0,255,  0):                     #? VERDE: Spawn Jogador
                                self.spawn_x = x * self.tile_size
                                self.spawn_y = y * self.tile_size
                            case (255,  0,  0): 
                                self.enemy_spawns.append((x,y))     #? VERMELHO: Inimigo
                            case (  0,  0,255):                     #? AZUL: Transição
                                pass
                            case (255,255,  0):                     #? AMARELO: Item
                                self.item_spawns.append((x,y))
        except FileNotFoundError:
            print(f"[MapModel] Erro: Imagem de meta-dados '{meta_filename}' não encontrada.")

    def is_wall(self, grid_x: int, grid_y: int) -> bool:
        if 0 <= grid_y < self.height_tiles and 0 <= grid_x < self.width_tiles:
            return self.collision_grid[grid_y][grid_x]
        return True

    def get_tile_at(self, pixel_x:float,pixel_y:float)->str:
        grid_x = int(pixel_x // self.tile_size)
        grid_y = int(pixel_y // self.tile_size)
        return f"{grid_x},{grid_y}"
