
import pygame as PYG
import os

from src.Config import CONTENT_DIR

class DialogSystem:
    def __init__(self, screen: PYG.Surface):
        self.screen = screen
        self.active = False
        self.lines: list[str] = []
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.char_timer = 0.0
        self.char_delay = 0.03  #? Velocidade do texto (segundos por letra)
        self.state = "IDLE"     #? Estados: IDLE, TYPING, WAITING
        self.box_height = 160
        self.margin = 20
        self.sfx_voice = PYG.Sound(os.path.join(CONTENT_DIR, "sound", "meow-1.mp3"))
        self.sfx_voice.set_volume(0.5)
        self.font = PYG.font.Font(os.path.join(CONTENT_DIR, "font", "KiwiSoda.ttf"), size=28) 

    def start_dialog(self, lines: list[str]):
        if not lines: return
        self.lines = lines
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.char_timer = 0.0
        self.active = True
        self.state = "TYPING"

    def advance(self):
        if not self.active: return
        if self.state == "TYPING":
            self.current_char_idx = len(self.lines[self.current_line_idx])
            self.state = "WAITING"
        elif self.state == "WAITING":
            self.current_line_idx += 1
            if self.current_line_idx >= len(self.lines):
                self.active = False
                self.state = "IDLE"
            else:
                self.current_char_idx = 0
                self.char_timer = 0.0
                self.state = "TYPING"

    def update(self, dt: float):
        if not self.active or self.state != "TYPING": return
        self.char_timer += dt
        if self.char_timer >= self.char_delay:
            self.char_timer = 0.0
            self.current_char_idx += 1
            if self.current_char_idx >= len(self.lines[self.current_line_idx]):
                self.current_char_idx = len(self.lines[self.current_line_idx])
                self.state = "WAITING"

    def draw(self):
        if not self.active: return
        sw, sh = self.screen.get_size()
        box_rect = PYG.Rect(self.margin, sh - self.box_height - self.margin, sw - (self.margin * 2), self.box_height)
        PYG.draw.rect(self.screen, (0, 0, 0), box_rect)
        PYG.draw.rect(self.screen, (255, 255, 255), box_rect, width=4)
        if self.current_line_idx < len(self.lines):
            full_text = self.lines[self.current_line_idx]
            visible_text = full_text[:self.current_char_idx]
            display_text = f"* {visible_text}"
            words = display_text.split('\n')
            for i, line in enumerate(words):
                text_surf = self.font.render(line, True, (255, 255, 255))
                self.sfx_voice.play()
                self.screen.blit(text_surf, (box_rect.x + 25, box_rect.y + 25 + (i * 35)))
            if self.state == "WAITING":
                indicator = self.font.render(">", True, (255, 255, 255))
                if PYG.time.get_ticks() % 1000 < 500:
                    self.screen.blit(indicator, (box_rect.right - 40, box_rect.bottom - 40))
