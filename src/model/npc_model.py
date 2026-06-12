import pygame as PYG

class NPCModel:
    def __init__(self, x: float, y: float, size: int = 32) -> None:
        self.rect = PYG.Rect(int(x), int(y), size, size)
        self.hitbox = PYG.Rect(0, 0, 32, 32)
        self.hitbox.center = self.rect.center
        self.is_interacting = False
        self.dialog = "Olá, Raposa! Pressione E novamente para sair."
    
    def interact(self):
        self.is_interacting = not self.is_interacting
        if self.is_interacting: print(f"[NPC] {self.dialog}")
        else: print("[NPC] Até Raposa, cuide do meu humano!")
