
import pygame as PYG
from src.Config import WINDOW_TITLE, SCREEN_SIZE, FPS, RESIZABLE, GameState
from src.controller.Start_screen_controller import StartScreenController
from src.controller.playing_controller import PlayingController

class Core:
    def __init__(self):
        PYG.init()
        PYG.mixer.init()
        
        flags = PYG.RESIZABLE if RESIZABLE else 0
        self.screen = PYG.display.set_mode(tuple(SCREEN_SIZE), flags)
        PYG.display.set_caption(WINDOW_TITLE)
        
        self.clock = PYG.time.Clock()
        self.running = True
        
        self._state = GameState.START_SCREEN
        self._controllers = {}
        self._load_controllers()
    
    def _load_controllers(self):
        self._controllers = {
            GameState.START_SCREEN: StartScreenController(
                screen=self.screen,
                change_state_cb=self.change_state
            ),
            GameState.PLAYING: PlayingController(
                screen=self.screen,
                change_state_cb=self.change_state
            ) 
        }
    
    def change_state(self, new_state: str):
        if new_state == GameState.PLAYING and new_state not in self._controllers:
            raise NotImplementedError(f"Controller para '{new_state}' ainda não implementado.")
        match new_state:
            case GameState.START_SCREEN:
                ...
            case GameState.PLAYING:
                ...
        self._state = new_state
    
    @property
    def active_controller(self): return self._controllers.get(self._state)
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            
            events = PYG.event.get()
            for event in events:
                if event.type == PYG.QUIT: self.running = False
            
            if self.active_controller:
                self.active_controller.handle_events(events)
                self.active_controller.update(delta_time)
                self.active_controller.draw()
            
            PYG.display.flip()
        self._quit()
    
    def _quit(self):
        PYG.mixer.quit()
        PYG.quit()
