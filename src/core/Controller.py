
from __future__ import annotations
from typing import Callable, List
import pygame as PYG

class Controller:
    def __init__(
        self,
        screen: PYG.Surface,
        change_state_cb: Callable[[str], None],
    ):
        self.screen = screen
        self.change_state = change_state_cb
    
    def handle_events(self, events: List[PYG.event.Event]): raise NotImplementedError
    def update(self, delta_time: float): raise NotImplementedError
    def draw(self): raise NotImplementedError