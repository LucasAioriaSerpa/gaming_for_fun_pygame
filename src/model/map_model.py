
import json
import os
from src.Config import DATA_DIR

class MapModel:
    def __init__(self, filename: str, tile_size: int = 32):
        self.tile_size = tile_size
        self.transitions = {}
        self.grid = []
        self.spawn_x = 0.0
        self.spawn_y = 0.0
        
        self._load_map_from_json(filename)
    
    def _load_map_from_json(self, filename: str):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        raw_grid = data.get("grid", [])
        self.transitions = data.get("transitions", {})
        self.grid = [list(row) for row in raw_grid]
        self.width_pixels = len(self.grid[0]) * self.tile_size
        self.height_pixels = len(self.grid) * self.tile_size
        
        self._find_and_set_spawn()
    
    def _find_and_set_spawn(self):
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile_type in enumerate(row):
                match tile_type:
                    case "P":
                        self.spawn_x = col_idx * self.tile_size
                        self.spawn_y = row_idx * self.tile_size
                        self.grid[row_idx][col_idx] = '.'
                        return
    
    def is_wall(self, grid_x: int, grid_y:  int) -> bool:
        if 0 <= grid_y < len(self.grid) and 0 <= grid_x < len(self.grid[0]):
            return self.grid[grid_y][grid_x] == "X"
        return True
    
    def get_tile_at(self, pixel_x: int, pixel_y: int) -> bool:
        grid_x = int(pixel_x // self.tile_size)
        grid_y = int(pixel_y // self.tile_size)
        if 0 <= grid_y < len(self.grid) and 0 <= grid_x < len(self.grid[0]):
            return self.grid[grid_y][grid_x]
        return "X"
