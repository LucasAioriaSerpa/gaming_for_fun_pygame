
from __future__ import annotations

from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import random
import math

from src.view.View import View
from src.Config import (
    Colors, WINDOW_TITLE,
    FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_SMALL,
    SCREEN_SIZE
)

@dataclass
class Particle:
    x: float
    y: float
    speed: float
    size: float
    phase: float

BTN_NTUPLE = nTuple("BTN_NTUPLE", "WIDTH HEIGHT GAP RADIUS")

class StartScreenView(View):
    BTN = BTN_NTUPLE(
        260, 58,    #? WIDTH + HEIGHT
        18,         #? GAP
        14          #? RADIUS
    )

    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.font_title = PYG.font.SysFont(None, FONT_SIZE_TITLE, bold=True)
        self.font_btn = PYG.font.SysFont(None, FONT_SIZE_LARGE - 10, bold=True)
        self.font_hint = PYG.font.SysFont(None, FONT_SIZE_SMALL)
        self._buttons: list[str] = []
        self._hovered: str | None = None
        self._btn_rects: dict[str, PYG.Rect] = {}
        self._time = 0.0
        self._partiples = self._create_particles(60)
        self._title_alpha = 0
        self._btn_alpha = 0
        self._bg = self._make_gradient()
        
    def set_buttons(self, labels: list[str]):
        self._buttons = labels
        self._compute_btn_rects()

    def _compute_btn_rects(self):
        #* total_h = len(self._buttons) * self.BTN.HEIGHT + (len(self._buttons) - 1) * self.BTN.GAP
        start_y = self.height // 2 + 60
        cx = self.width // 2
        self._btn_rects = {}
        for i, label in enumerate(self._buttons):
            y = start_y + i * (self.BTN.HEIGHT + self.BTN.GAP)
            rect = PYG.Rect(0, 0, self.BTN.WIDTH, self.BTN.HEIGHT)
            rect.center = (cx, y)
            self._btn_rects[label] = rect

    @staticmethod
    def _create_particles(n: int) -> list[Particle]:
        rng = random.Random(42)
        return [
            Particle(
                x=rng.uniform(0, SCREEN_SIZE.WIDTH),
                y=rng.uniform(0, SCREEN_SIZE.HEIGHT),
                speed=rng.uniform(0, 30),
                size= rng.uniform(1, 3.5),
                phase=rng.uniform(0, math.tau)
            )
            for _ in range(n)
        ]

    def _update_particles(self, delta_time: float):
        for p in self._partiples:
            p.y -= p.speed * delta_time
            if p.y < -10:
                p.y = self.height + 10
                p.x = random.uniform(0, self.width)

    def _make_gradient(self) -> PYG.Surface:
        surf = PYG.Surface((self.width, self.height))
        top = Colors.BG
        bottom = (8, 5, 18)
        for y in range(self.height):
            t = y / self.height
            R = int(top[0] + (bottom[0] - top[0] * t))
            G = int(top[1] + (bottom[1] - top[1] * t))
            B = int(top[2] + (bottom[2] - top[2] * t))
            PYG.draw.line(surf, (R, G, B), (0, y), (self.width, y))
        return surf

    def get_clicked_button(self, mouse_pos: tuple[int, int]) -> str | None:
        for label, rect in self._btn_rects.items():
            if rect.collidepoint(mouse_pos): return label
        return None

    def update_hover(self, mouse_pos: tuple[int, int]):
        self._hovered = None
        for label, rect in self._btn_rects.items():
            if rect.collidepoint(mouse_pos): 
                self._hovered = label
                return label
        return None

    def update(self, delta_time:float):
        self._time += delta_time
        self._update_particles(delta_time)
        self._title_alpha = min(255, self._title_alpha + int(255 * delta_time / 1.2))
        self._btn_alpha = min(255, self._btn_alpha + int(255 * delta_time / 1.8))

    def draw(self):
        self.screen.blit(self._bg, (0, 0))
        self._draw_particles()
        self._draw_decorative_lines()
        self._draw_title()
        self._draw_subtitle()
        self._draw_buttons()
        self._draw_hint()

    def _draw_particles(self):
        for p in self._partiples:
            alpha = int(120 + 80 * math.sin(self._time * 0.8 + p.phase))
            size = p.size
            surf = PYG.Surface((int(size * 2 + 2), int(size * 2 + 2)), PYG.SRCALPHA)
            PYG.draw.circle(surf, (*Colors.ACCENT, alpha), (int(size + 1), int(size + 1)), int(size))
            self.screen.blit(surf, (int(p.x - size), int(p.y - size)))

    def _draw_decorative_lines(self):
        cx = self.width // 2
        y = self.height // 2 - 110
        alpha = int(60 + 40 * math.sin(self._time))
        surf = PYG.Surface((400, 2), PYG.SRCALPHA)
        surf.fill((*Colors.ACCENT, alpha))
        self.screen.blit(surf, (cx - 200, y))

    def _draw_title(self):
        cx, cy = self.width // 2, self.height // 2 - 60
        shadow = self.font_title.render(WINDOW_TITLE.upper(), True, Colors.ACCENT)
        shadow.set_alpha(min(self._title_alpha, 80))
        sr = shadow.get_rect(center=(cx+4, cy+4))
        self.screen.blit(shadow, sr)
        self.draw_text(WINDOW_TITLE.upper(), self.font_title, Colors.TEXT,
                        (cx, cy), alpha=self._title_alpha)

    def _draw_subtitle(self):
        tagline = "Pressione ENTER para jogar"
        pulse = int(160 + 80 * math.sin(self._time * 2.0))
        self.draw_text(tagline, self.font_hint, Colors.TEXT_DIM,
                        (self.width // 2, self.height // 2 + 5), alpha=min(self._btn_alpha, pulse))

    def _draw_buttons(self):
        for label, rect in self._btn_rects.items():
            is_hover = (label == self._hovered)
            
            bg_color = Colors.ACCENT if is_hover else (30, 25, 50)
            border_color = Colors.ACCENT if is_hover else Colors.ACCENT2
            self.draw_rect_aa(bg_color, rect, border_radius=self.BTN.RADIUS,
                                alpha=min(self._btn_alpha, 210 if is_hover else 160))
            
            PYG.draw.rect(self.screen, border_color, rect,
                            width=2, border_radius=self.BTN.RADIUS)
            
            offset = -2 if is_hover else 0
            text_color = Colors.WHITE if is_hover else Colors.TEXT
            self.draw_text(label, self.font_btn, text_color,
                            (rect.centerx, rect.centery + offset),
                            alpha=self._btn_alpha)
        
    def _draw_hint(self):
        hint = "ESC - Sair"
        self.draw_text(hint, self.font_hint, Colors.TEXT_DIM,
                        (self.width // 2, self.height - 28),
                        alpha=min(self._btn_alpha, 140))
