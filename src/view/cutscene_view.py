
from __future__ import annotations
from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import os

from src.view.View import View
from src.Config import SCREEN_SIZE, SCREEN_ZOOM

class CutSceneView(View):
    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self.screen = screen
        self.internal_size = (SCREEN_SIZE.WIDTH/SCREEN_ZOOM[1], SCREEN_SIZE.HEIGHT/SCREEN_ZOOM[1])
        self.internal_surf = PYG.Surface(self.internal_size)
        self.bg_image = None
        self.fade_alpha = 255.0
        self.fade_surface = PYG.Surface(self.screen.get_size())
        self.fade_surface.fill((0, 0, 0))

    def load_background(self, image_path: str):
        if os.path.exists(image_path):
            img = PYG.image.load(image_path).convert()
            self.bg_image = PYG.transform.scale(img, self.screen.get_size())
        else:
            self.bg_image = PYG.Surface(self.screen.get_size())
            self.bg_image.fill((40, 40, 50))

    def update(self, delta_time: float): return super().update(delta_time)

    def draw(self):
        if self.bg_image: self.internal_surf.blit(self.bg_image, (0, 0))
        if self.fade_alpha > 0:
            alpha_int = max(0, min(255, int(self.fade_alpha)))
            self.fade_surface.set_alpha(alpha_int)
            self.internal_surf.blit(self.fade_surface, (0, 0))
        PYG.transform.scale(self.internal_surf, self.screen.get_size(), self.screen)
