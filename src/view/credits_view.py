
from __future__ import annotations
from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import json
import os

from src.view.View import View
from src.Config import CONTENT_DIR

class CreditsView(View):
    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.screen = screen
        font_file_path = os.path.join(CONTENT_DIR, "font", "8-bit Arcade In.ttf")
        self.font_title     = PYG.font.Font(font_file_path, 36*2)
        self.font_section   = PYG.font.Font(font_file_path, 24*2)
        self.font_name      = PYG.font.Font(font_file_path, 18*2)
        self.font_footer    = PYG.font.Font(font_file_path, 14*2)
        self.font_footer.italic = True
        self.text_lines = []
        self._load_credits_json()

    def _load_credits_json(self):
        json_path = os.path.join("data", "credits.json")
        if not os.path.exists(json_path):
            self.text_lines = [
                ("main_title", "CRÉDITOS"),
                ("space", 50),
                ("section", "Erro ao carregar data/credits.json")
            ]
            return
        with open(json_path, "r", encoding="utf-8") as f: data = json.load(f)
        self.text_lines.append(("main_title", data.get("title", "CRÉDITOS")))
        self.text_lines.append(("space", 50))
        for section in data.get("sections", []):
            self.text_lines.append(("section", section.get("title", "")))
            self.text_lines.append(("space", 15))
            for name in section.get("names", []):
                self.text_lines.append(("name", name))
            self.text_lines.append(("space", 45))
        self.text_lines.append(("space", 60))
        self.text_lines.append(("footer", "Pressione qualquer tecla ou clique para voltar"))

    def update(self, delta_time: float): return super().update(delta_time)

    def draw(self, scroll_y: float):
        self.screen.fill((0, 0, 0))
        sw, sh = self.screen.get_size()
        current_y = sh - scroll_y 
        for line_type, value in self.text_lines:
            match line_type:
                case "space":
                    current_y += value
                    continue
                case "main_title":
                    surf = self.font_title.render(value, True, (255, 255, 255))
                case "section":
                    surf = self.font_section.render(value, True, (255, 255, 0))
                case "name":
                    surf = self.font_name.render(value, True, (255, 255, 255))
                case "footer":
                    surf = self.font_footer.render(value, True, (150, 150, 150))
            rect = surf.get_rect(center=(sw // 2, current_y))
            if -50 < current_y < sh + 50:
                self.screen.blit(surf, rect)
            current_y += surf.get_height()
