
from __future__ import annotations

from dataclasses import dataclass
from collections import namedtuple as nTuple
import pygame as PYG
import random
import math

from src.view.View import View

class PlayingView(View):

    def __init__(self, screen: PYG.Surface):
        super().__init__(screen)
        self._time = 0.0
        self._bg = self._create_background_surface()

    def _create_background_surface(self):
        surf = PYG.Surface((self.width, self.height))
        surf.fill((0,0,0))
        return surf

    def update(self, delta_time:float):
        self._time += delta_time

    def draw(self):
        self.screen.blit(self._bg, (0, 0))
