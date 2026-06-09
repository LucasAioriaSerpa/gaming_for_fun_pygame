import pygame as PYG
import os
import json
from src.Config import CONTENT_DIR, DATA_DIR

_TILESET_CACHE: dict[str, dict[str, PYG.Surface]] = {}

def load_tile(filename: str, size: tuple[int, int] = (32, 32)) -> PYG.Surface:
    path = os.path.join(CONTENT_DIR, filename)
    try:
        image = PYG.image.load(path).convert_alpha()
        return PYG.transform.scale(image, size)
    except FileNotFoundError:
        print("[ load_tile ] - spreedsheet ou imagem n encontrada...")
        surf = PYG.Surface(size)
        surf.fill((225, 0, 255))
        return surf

def load_tileset(tileset_name: str, target_tile_size: int = 32) -> dict[str, PYG.Surface]:
    json_path = os.path.join(DATA_DIR, "tile_sets", f"{tileset_name}.json")
    tiles_dict = {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            ts_data = json.load(f)
        asset_path = ts_data.get("asset_path", "")
        source_tile_size = ts_data.get("tile_size", 32)
        tiles_config = ts_data.get("tiles", {})
        full_path = os.path.join(CONTENT_DIR, asset_path)
        spritesheet = PYG.image.load(full_path).convert_alpha()
        for tile_name, coords in tiles_config.items():
            gx = coords["grid_x"] * source_tile_size
            gy = coords["grid_y"] * source_tile_size
            rect = PYG.Rect(gx, gy, source_tile_size, source_tile_size)
            sub_surf = spritesheet.subsurface(rect)
            if source_tile_size != target_tile_size:
                sub_surf = PYG.transform.scale(sub_surf, (target_tile_size, target_tile_size))
            tiles_dict[tile_name] = sub_surf
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"[Erro no Tileset] Falha ao carregar o tileset {tileset_name}: {e}")
        fallback = PYG.Surface((target_tile_size, target_tile_size))
        fallback.fill((255, 0, 255))
        tiles_dict["fallback"] = fallback        
    return tiles_dict
