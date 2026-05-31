
from __future__ import annotations
from typing import Callable, List
import pygame as PYG

from src.core.Controller import Controller
from src.view.playing_view import PlayingView
from src.Config import GameState

class PlayingController(Controller):
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None]
    ):
        super().__init__(screen, change_state_cb)
        
        self.view = PlayingView(screen)
        
    def handle_events(self, events: List[PYG.event.Event]):
        mouse_pos = PYG.mouse.get_pos()
        
        for event in events:
            ...

    def update(self, delta_time: float): self.view.update(delta_time)
    
    def draw(self): self.view.draw()
