import json
import os
from src.Config import DATA_DIR

class MapModel:
    def __init__(self, filename: str, tile_size: int = 32):
        self.tile_size = tile_size
        self.transitions = {}
        self.ground_layer = []
        self.decor_low_layer = []
        self.decor_high_layer = []
        self.tileset_name = ""
        self.passable_tiles = set()
        self.spawn_x = 0.0
        self.spawn_y = 0.0
        self._load_map_from_json(filename)
    
    def _load_map_from_json(self, filename: str):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.tileset_name = data.get("tileset", "start_area")
        self.transitions = data.get("transitions", {})
        self._load_tileset_properties(self.tileset_name)    
        layers = data.get("layers", {})
        self.ground_layer = layers.get("ground", [])
        self.decor_low_layer = layers.get("decor_low", [])
        self.decor_high_layer = layers.get("decor_high", [])
        self.height_tiles = len(self.ground_layer)
        self.width_tiles = len(self.ground_layer[0]) if self.height_tiles > 0 else 0
        self.width_pixels = self.width_tiles * self.tile_size
        self.height_pixels = self.height_tiles * self.tile_size
        self.spawn_data = data.get("spawn", {"x": 1, "y": 1})
        self.spawn_x = self.spawn_data["x"] * self.tile_size
        self.spawn_y = self.spawn_data["y"] * self.tile_size
    
    def _load_tileset_properties(self, tileset_name: str):
        tileset_path = os.path.join(DATA_DIR, "tile_sets", f"{tileset_name}.json")
        if os.path.exists(tileset_path):
            with open(tileset_path, "r", encoding="utf-8") as f:
                ts_data = json.load(f)
            self.passable_tiles = set(ts_data.get("passable", []))
        else: 
            self.passable_tiles = set()
    
    def is_wall(self, grid_x: int, grid_y: int) -> bool:
        if 0 <= grid_y < self.height_tiles and 0 <= grid_x < self.width_tiles:
            tile_ground = self.ground_layer[grid_y][grid_x]
            if grid_y < len(self.decor_low_layer) and grid_x < len(self.decor_low_layer[grid_y]):
                tile_decor = self.decor_low_layer[grid_y][grid_x]
            else:
                tile_decor = "none"
            if tile_ground not in self.passable_tiles: 
                return True
            if tile_decor != "none" and tile_decor not in self.passable_tiles: 
                return True
            return False
        return True
    
    def get_tile_at(self, pixel_x: int, pixel_y: int) -> str:
        grid_x = int(pixel_x // self.tile_size)
        grid_y = int(pixel_y // self.tile_size)
        return f"{grid_x},{grid_y}"
