
from __future__ import annotations
from typing import Callable, List
import pygame as PYG
import os

from src.core.Controller import Controller
from src.view.Start_screen_view import StartScreenView
from src.Config import CONTENT_DIR, GameState

class StartScreenController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        super().__init__(screen, change_state_cb)
        PYG.mixer.music.fadeout(3)
        PYG.mixer.music.unload()
        PYG.mixer.music.load(os.path.join(CONTENT_DIR, "sound", "music", "another_him.mp3"))
        PYG.mixer.music.set_volume(0.8)
        PYG.mixer.music.play(loops=-1, fade_ms=5)
        self.view = StartScreenView(screen)
        self._buttons = {
            "Jogar": self._on_play,
            "Sair": self._on_quit
        }
        self.view.set_buttons(list(self._buttons.keys()))
        
    def _on_play(self): self.change_state(GameState.PLAYING)
    
    def _on_quit(self): PYG.event.post(PYG.event.Event(PYG.QUIT))
    
    def handle_events(self, events: List[PYG.event.Event]):
        mouse_pos = PYG.mouse.get_pos()
        self.view.update_hover(mouse_pos)
        
        for event in events:
            if event.type == PYG.MOUSEBUTTONDOWN and event.button == 1:
                clicked = self.view.get_clicked_button(mouse_pos)
                if clicked and clicked in self._buttons: self._buttons[clicked]()
            
            if event.type == PYG.KEYDOWN:
                if event.key == PYG.K_RETURN: self._on_play()
                elif event.key == PYG.K_ESCAPE: self._on_quit()
    
    def update(self, delta_time: float): self.view.update(delta_time)
    
    def draw(self): self.view.draw()
