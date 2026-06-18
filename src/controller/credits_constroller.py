
from __future__ import annotations
from typing import Callable, List
import pygame as PYG
import os

from src.core.Controller import Controller
from src.view.credits_view import CreditsView
from src.Config import GameState, CONTENT_DIR

class CreditsController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        self.change_state_cb = change_state_cb
        super().__init__(screen, change_state_cb)
        self.view = CreditsView(screen)
        self.scroll_y = 0.0
        self.scroll_speed = 50.0
        self._play_background_music()

    def _play_background_music(self):
        PYG.mixer.music.fadeout(3)
        PYG.mixer.music.unload()
        PYG.mixer.music.load(os.path.join(CONTENT_DIR, "sound", "music", "dogSong.mp3"))
        PYG.mixer.music.set_volume(1)
        PYG.mixer.music.play(loops=-1, fade_ms=3)

    def on_enter(self): self.__init__(self.screen, self.change_state_cb); self.scroll_y = 0.0

    def handle_events(self, events: List[PYG.event.Event]):
        for event in events:
            if event.type == PYG.KEYDOWN:           self.change_state(GameState.START_SCREEN)
            elif event.type == PYG.MOUSEBUTTONDOWN: self.change_state(GameState.START_SCREEN)

    def update(self, delta_time: float): self.scroll_y += self.scroll_speed * delta_time

    def draw(self): self.view.draw(self.scroll_y)