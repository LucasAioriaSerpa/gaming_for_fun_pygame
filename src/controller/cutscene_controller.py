
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
        super().__init__(screen, change_state_cb)
        self.view = CutSceneView(screen)
        self.dialog_system = DialogSystem(screen)
        self.fade_alpha = 255.0
        self.fade_speed = 120.0
        self.is_fading_out = False
        self.bg_image_path = os.path.join(CONTENT_DIR, "cutscene", "cutscene.png")
        self.dialog_lines = [
            "ah.. você me encontrou...",
            "..mesmo, depois de tudo.. ?",
            "desculp por causar tantos problemas pra ti...",
            "..eu não sei o que eu seria sem você..",
            "...contigo eu sei que em meus piores dias eu terei a ti...",
            "..assim como no seus piores dias você tera a mim..",
            "...vamos.. passar por essa juntos..",
            "...como..",
            "..sempre <3",
            "te amo minha raposinha~",
            "vamos..\n temos muitas coisas pra fazer juntos <3"
        ]

    def _play_background_music(self):
        PYG.mixer.music.fadeout(3)
        PYG.mixer.music.unload()
        PYG.mixer.music.load(os.path.join(CONTENT_DIR, "sound", "music", "dontForget_musicBox.mp3"))
        PYG.mixer.music.set_volume(1)
        PYG.mixer.music.play(loops=-1, fade_ms=3)

    def on_enter(self):
        self.fade_alpha = 255.0
        self.is_fading_out = False
        self.view.load_background(self.bg_image_path)
        self.dialog_system.start_dialog(
            PYG.font.Font(os.path.join(CONTENT_DIR, "font", "Mojang-Bold.ttf"), size=28),
            PYG.Sound(os.path.join(CONTENT_DIR, "sound", "voice_talking.wav")),
            self.dialog_lines
        )
        self._play_background_music()

    def handle_events(self, events: List[PYG.event.Event]):
        for event in events:
            if event.type == PYG.KEYDOWN:
                if event.key in (PYG.K_e, PYG.K_RETURN, PYG.K_SPACE):
                    self.dialog_system.advance()
                elif event.key == PYG.K_ESCAPE:
                    self.is_fading_out = True
            elif event.type == PYG.MOUSEBUTTONDOWN and event.button == 1:
                self.dialog_system.advance()

    def update(self, delta_time: float):
        self.dialog_system.update(delta_time)
        if not self.is_fading_out:
            if self.fade_alpha > 0:
                self.fade_alpha -= self.fade_speed * delta_time
                if self.fade_alpha < 0:
                    self.fade_alpha = 0
            if self.fade_alpha <= 0 and not self.dialog_system.active:
                self.is_fading_out = True
        else:
            if self.fade_alpha < 255:
                self.fade_alpha += self.fade_speed * delta_time
            else:
                self.fade_alpha = 255
                self.change_state(GameState.CREDITS)

    def draw(self):
        self.view.draw(self.fade_alpha)
        self.dialog_system.draw()
