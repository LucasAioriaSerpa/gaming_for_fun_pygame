import pygame as PYG
import json
import os

from src.Config import DATA_DIR, CONTENT_DIR

class NPCModel:
    def __init__(self, file_info: str, x: float, y: float, size: int = 32) -> None:
        self.x = x
        self.y = y
        self.rect = PYG.Rect(int(x), int(y), size, size)
        self.hitbox = PYG.Rect(0, 0, 32, 32)
        self.hitbox.center = self.rect.center
        self.is_interacting = False
        self._load_npc_info(file_info)
    
    def _load_npc_info(self, file_info: str):
        file_path_data = os.path.join(DATA_DIR, "npcs")
        with open(os.path.join(file_path_data, file_info), "r", encoding="utf-8") as f:
            data = json.load(f)
        self.font_voice   = PYG.font.Font(os.path.join(CONTENT_DIR, "font",  data.get("font")), size=28)
        self.sfx_voice    = PYG.Sound(os.path.join(CONTENT_DIR, "sound", data.get("sfx_voice")))
        self.dialog_lines = data.get("dialog")
        
    
    def interact(self): return self.dialog_lines
