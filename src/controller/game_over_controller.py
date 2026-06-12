
from __future__ import annotations
from typing import Callable

import pygame as PYG

from src.core.Controller import Controller
from src.view.game_over_view import GameOverView
from src.Config import GameState

class GameOverController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        super().__init__(screen, change_state_cb)
        self.view = GameOverView(screen)
        self._actions = {
            "Tentar Novamente": self._on_retry,
            "Menu Principal": self._on_menu
        }
        self.view.set_buttons(list(self._actions.keys()))

    def _on_retry(self): self.change_state(GameState.PLAYING)
    
    def _on_menu(self): self.change_state(GameState.START_SCREEN)

    def on_enter(self): self.view.reset()

    def handle_events(self, events: list[PYG.event.Event]):
        for event in events:
            if event.type == PYG.MOUSEMOTION:
                self.view.update_hover(event.pos)
            elif event.type == PYG.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    clicked = self.view.get_clicked_button(event.pos)
                    if clicked in self._actions:
                        self._actions[clicked]()
            elif event.type == PYG.KEYDOWN:
                if event.key == PYG.K_RETURN:
                    self._actions["Tentar Novamente"]()
                elif event.key == PYG.K_ESCAPE:
                    self._actions["Menu Principal"]()

    def update(self, delta_time: float): self.view.update(delta_time)

    def draw(self): self.view.draw()
