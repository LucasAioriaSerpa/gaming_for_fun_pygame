
from __future__ import annotations
import pygame as PYG

from src.Config import Colors

class View:
    def __init__(self, screen: PYG.Surface):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

    def update(self, delta_time: float): raise NotImplementedError
    
    def draw(self): raise NotImplementedError
    
    def draw_text(
        self,
        text: str,
        font: PYG.font.Font,
        color,
        center: tuple[int, int],
        alpha: int = 255,
    ) -> PYG.Rect:
        surface = font.render(text, True, color)
        if alpha < 255: surface.set_alpha(alpha)
        rect = surface.get_rect(center=center)
