
from __future__ import annotations
from typing import Callable, List
import pygame as PYG
import os

from src.core.Controller import Controller
from src.view.cutscene_view import CutSceneView
from src.ui.dialogSystem import DialogSystem
from src.Config import GameState, CONTENT_DIR

class CutSceneController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        self.change_state_cb = change_state_cb
        super().__init__(screen, change_state_cb)
        self.view = CutSceneView(screen)
        self.dialog_system = DialogSystem(screen)
        self.fade_alpha = 255.0
        self.fade_speed = 120.0
        self.bg_image_path = "assets/images/cutscene_bg.png"
        self.dialog_lines = [
            "E assim, a jornada chega ao seu fim.",
            "O reino está a salvo mais uma vez...",
            "Mas novas aventuras aguardam no horizonte.",
            "Obrigado por jogar!"
        ]
        self._play_background_music()

    def _play_background_music(self):
        PYG.mixer.music.fadeout(3)
        PYG.mixer.music.unload()
        PYG.mixer.music.load(os.path.join(CONTENT_DIR, "sound", "music", "dontForget_musicBox.mp3"))
        PYG.mixer.music.set_volume(1)
        PYG.mixer.music.play(loops=-1, fade_ms=3)

    def on_enter(self):
        self.__init__(self.screen, self.change_state_cb)
        self.fade_alpha = 255.0
        self.view.load_background(self.bg_image_path)
        self.dialog_system.start_dialog(
            PYG.font.Font(os.path.join(CONTENT_DIR, "font", "Mojang-Bold.ttf"), size=28),
            PYG.Sound(os.path.join(CONTENT_DIR, "sound", "voice_talking.wav")),
            self.dialog_lines
        )

    def handle_events(self, events: List[PYG.event.Event]):
        for event in events:
            if event.type == PYG.KEYDOWN:
                if event.key in (PYG.K_e, PYG.K_RETURN, PYG.K_SPACE):
                    self.dialog_system.advance()
                elif event.key == PYG.K_ESCAPE:
                    self.change_state(GameState.CREDITS)
            elif event.type == PYG.MOUSEBUTTONDOWN and event.button == 1:
                self.dialog_system.advance()

    def update(self, delta_time: float):
        if self.fade_alpha > 0:
            self.fade_alpha -= self.fade_speed * delta_time
            if self.fade_alpha < 0:
                self.fade_alpha = 0
        self.dialog_system.update(delta_time)
        if self.fade_alpha <= 0 and not self.dialog_system.active:
            self.change_state(GameState.CREDITS)

    def draw(self):
        self.view.draw()
        self.dialog_system.draw()
