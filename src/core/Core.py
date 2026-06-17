
import pygame as PYG
import asyncio

from src.Config import CONTENT_DIR, WINDOW_TITLE, SCREEN_SIZE, FPS, RESIZABLE, GameState
from src.controller.Start_screen_controller import StartScreenController
from src.controller.playing_controller      import PlayingController
from src.controller.game_over_controller    import GameOverController
from src.controller.cutscene_controller     import CutSceneController
from src.controller.credits_constroller     import CreditsController

class Core:
    def __init__(self):
        PYG.init()
        PYG.mixer.init()
        PYG.mixer.Channel(0) #* Button Select / Button Click
        PYG.mixer.Channel(1) #* attaque
        PYG.mixer.Channel(2) #* attaque inimigo
        PYG.mixer.Channel(3) #* Dano Jogador
        PYG.mixer.Channel(4) #* Dano Inimigo
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
            GameState.CREDITS: CreditsController(
                screen=self.screen,
                change_state_cb=self.change_state   
            ),
            GameState.CUTSCENE: CutSceneController(
                screen=self.screen,
                change_state_cb=self.change_state
            ),
            GameState.GAME_OVER: GameOverController(
                screen=self.screen,
                change_state_cb=self.change_state
            ),
            GameState.PLAYING: PlayingController(
                screen=self.screen,
                change_state_cb=self.change_state
            ),
            GameState.START_SCREEN: StartScreenController(
                screen=self.screen,
                change_state_cb=self.change_state
            ),
        }
    
    def change_state(self, new_state: str):
        PYG.mixer.music.unload()
        if new_state not in self._controllers:
            raise NotImplementedError(f"Controller para '{new_state}' ainda não implementado.")
        self._state = new_state
        controller = self.active_controller
        if controller and hasattr(controller, "on_enter"): controller.on_enter()
    
    @property
    def active_controller(self): return self._controllers.get(self._state)
    
    async def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0
            events = PYG.event.get()
            for event in events:
                if event.type == PYG.QUIT: self.running = False
            current_controller = self.active_controller
            if current_controller:
                current_controller.handle_events(events)
                current_controller.update(delta_time)
                current_controller.draw()
            PYG.display.flip()
            await asyncio.sleep(0)
        self._quit()
    
    def _quit(self):
        PYG.mixer.quit()
        PYG.quit()
