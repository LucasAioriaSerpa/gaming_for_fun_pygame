from __future__ import annotations
from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import random
import math
import os

from src.view.View import View
from src.Config import (
    Colors, FONT_SIZE_TITLE, FONT_SIZE_LARGE, FONT_SIZE_SMALL, SCREEN_SIZE, CONTENT_DIR
)

@dataclass
class _Ember:
    x:     float
    y:     float
    speed: float
    size:  float
    phase: float
    drift: float

BTN_NTUPLE = nTuple("BTN_NTUPLE", "WIDTH HEIGHT GAP RADIUS")

class GameOverView(View):
    BTN = BTN_NTUPLE(290, 58, 16, 14)
    _BG_TOP    = ( 22,  5,  5)
    _BG_BOT    = (  4,  0,  0)
    _C_TITLE   = Colors.FOX_RED_ORG
    _C_SHADOW  = Colors.FOX_MAGENTA
    _C_EMBER   = Colors.FOX_RED_ORG
    _C_BORDER  = Colors.FOX_MAGENTA
    _C_HOVER   = Colors.FOX_RED_ORG

    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.font_title    = PYG.font.SysFont(None, FONT_SIZE_TITLE + 12, bold=True)
        self.font_subtitle = PYG.font.SysFont(None, FONT_SIZE_SMALL + 4)
        self.font_btn      = PYG.font.SysFont(None, FONT_SIZE_LARGE - 10, bold=True)
        self.font_hint     = PYG.font.SysFont(None, FONT_SIZE_SMALL)
        self._buttons: list[str] = []
        self._hovered: str | None = None
        self._btn_rects: dict[str, PYG.Rect]  = {}
        self._time      = 0.0
        self._embers    = self._spawn_embers(155)
        self._alpha     = 0
        self._btn_alpha = 0
        self._bg = self._make_gradient()

    def set_buttons(self, labels: list[str]):
        self._buttons = labels
        self._compute_btn_rects()

    def _compute_btn_rects(self):
        start_y = self.height // 2 + 50
        cx      = self.width  // 2
        self._btn_rects = {}
        for i, label in enumerate(self._buttons):
            y    = start_y + i * (self.BTN.HEIGHT + self.BTN.GAP)
            rect = PYG.Rect(0, 0, self.BTN.WIDTH, self.BTN.HEIGHT)
            rect.center = (cx, y)
            self._btn_rects[label] = rect

    def reset(self):
        self._time = self._alpha = self._btn_alpha = 0.0
        rng = random.Random(77)
        for e in self._embers:
            e.x, e.y = rng.uniform(0, self.width), rng.uniform(0, self.height)

    @staticmethod
    def _spawn_embers(n: int) -> list[_Ember]:
        rng = random.Random(77)
        return [
            _Ember(
                x=rng.uniform(0, SCREEN_SIZE.WIDTH),
                y=rng.uniform(0, SCREEN_SIZE.HEIGHT),
                speed=rng.uniform(18, 55),
                size=rng.uniform(0.8, 2.8),
                phase=rng.uniform(0, math.tau),
                drift=rng.uniform(-30, 30),
            )
            for _ in range(n)
        ]

    def _make_gradient(self) -> PYG.Surface:
        surf = PYG.Surface((self.width, self.height))
        t_r, b_r = self._BG_TOP, self._BG_BOT
        for y in range(self.height):
            t = y / self.height
            r = int(t_r[0] + (b_r[0] - t_r[0]) * t)
            g = int(t_r[1] + (b_r[1] - t_r[1]) * t)
            b = int(t_r[2] + (b_r[2] - t_r[2]) * t)
            PYG.draw.line(surf, (r, g, b), (0, y), (self.width, y))
        return surf

    def get_clicked_button(self, pos: tuple) -> str | None:
        for label, rect in self._btn_rects.items():
            if rect.collidepoint(pos): 
                PYG.mixer.Channel.play(PYG.mixer.Channel(0), PYG.mixer.Sound(os.path.join(CONTENT_DIR, "sound", "savepoint.mp3")))
                return label
        return None

    def update_hover(self, pos: tuple):
        self._hovered = None
        for label, rect in self._btn_rects.items():
            if rect.collidepoint(pos):
                PYG.mixer.Channel.play(PYG.mixer.Channel(0), PYG.mixer.Sound(os.path.join(CONTENT_DIR, "sound", "sqek.mp3")))
                self._hovered = label
                break

    def update(self, dt: float):
        self._time      += dt
        self._alpha     = min(255, self._alpha     + int(255 * dt / 0.7))
        self._btn_alpha = min(255, self._btn_alpha + int(255 * dt / 1.3))
        for e in self._embers:
            e.y += e.speed * dt
            e.x += e.drift * dt * 0.15 * math.sin(self._time * 0.6 + e.phase)
            if e.y > self.height + 10:
                e.y = -10
                e.x = random.uniform(0, self.width)

    def draw(self):
        self.screen.blit(self._bg, (0, 0))
        self._draw_embers()
        self._draw_dec_line()
        self._draw_title()
        self._draw_subtitle()
        self._draw_buttons()
        self._draw_hint()

    def _draw_embers(self):
        for e in self._embers:
            alpha = int(70 + 55 * math.sin(self._time * 1.4 + e.phase))
            sz    = e.size
            s     = PYG.Surface((int(sz * 2 + 2), int(sz * 2 + 2)), PYG.SRCALPHA)
            PYG.draw.circle(s, (*self._C_EMBER, alpha), (int(sz + 1), int(sz + 1)), int(sz))
            self.screen.blit(s, (int(e.x - sz), int(e.y - sz)))

    def _draw_dec_line(self):
        cx  = self.width // 2
        y   = self.height // 2 - 105
        alp = int(50 + 35 * math.sin(self._time * 1.5))
        s   = PYG.Surface((380, 2), PYG.SRCALPHA)
        s.fill((*self._C_SHADOW, alp))
        self.screen.blit(s, (cx - 190, y))

    def _draw_title(self):
        cx, cy = self.width // 2, self.height // 2 - 65
        shadow = self.font_title.render("GAME OVER", True, self._C_SHADOW)
        shadow.set_alpha(min(self._alpha, 130))
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 6, cy + 6)))
        shadow2 = self.font_title.render("GAME OVER", True, self._C_SHADOW)
        shadow2.set_alpha(min(self._alpha, 60))
        self.screen.blit(shadow2, shadow2.get_rect(center=(cx - 3, cy + 3)))
        self.draw_text("GAME OVER", self.font_title, self._C_TITLE, (cx, cy), alpha=self._alpha)

    def _draw_subtitle(self):
        pulse = int(130 + 80 * math.sin(self._time * 1.8))
        self.draw_text(
            "Você foi derrotado",
            self.font_subtitle,
            Colors.TEXT_DIM,
            (self.width // 2, self.height // 2 - 14),
            alpha=min(self._btn_alpha, pulse),
        )

    def _draw_buttons(self):
        for label, rect in self._btn_rects.items():
            is_hover   = (label == self._hovered)
            bg_col     = self._C_HOVER  if is_hover else (35, 8, 8)
            bord_col   = self._C_HOVER  if is_hover else self._C_BORDER
            self.draw_rect_aa(bg_col, rect, border_radius=self.BTN.RADIUS,
                            alpha=min(self._btn_alpha, 215 if is_hover else 145))
            PYG.draw.rect(self.screen, bord_col, rect, width=2, border_radius=self.BTN.RADIUS)
            text_col = Colors.WHITE if is_hover else Colors.TEXT
            offset   = -2 if is_hover else 0
            self.draw_text(label, self.font_btn, text_col,
                            (rect.centerx, rect.centery + offset), alpha=self._btn_alpha)

    def _draw_hint(self):
        self.draw_text(
            "ENTER — Tentar Novamente  ·  ESC — Menu",
            self.font_hint, Colors.TEXT_DIM,
            (self.width // 2, self.height - 28),
            alpha=min(self._btn_alpha, 130),
        )
