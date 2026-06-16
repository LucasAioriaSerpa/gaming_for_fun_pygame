import pygame as PYG

class NPCModel:
    def __init__(self, x: float, y: float, size: int = 32) -> None:
        self.x = x
        self.y = y
        self.rect = PYG.Rect(int(x), int(y), size, size)
        self.hitbox = PYG.Rect(0, 0, 32, 32)
        self.hitbox.center = self.rect.center
        self.is_interacting = False
        self.dialog_lines = [
            "zZZZzzzZzZzZZz-\n  ah..",
            "Olá, Raposa",
            "Acredito que seja você que ele tanto fala..",
            "infelizmente tive que ir e deixa-lo",
            "não sei como ele tenha lidado com isto...",
            "desta vez não posso cuida-lo",
            "poderia cuidar do meu humano por favor?",
            "as vezes ele pode ser emocional\n  e lidar como fosse o fim do mundo",
            "tive que morder a cenela dele multiplas vezes pra ele me alimentar..",
            "ai ai.. humanos",
            "bem..\n  vá até ele",
            "sei que tu consegue Raposa",
            "se cuide\n  você é muito importante pra ele",
            "as emoções dele acabaram escapando",
            "eles podem ser agressivos\napertando o botão direito do mouse\n(seja lá oq isso for)",
            "você consegue desparar um pouco de ''ESPERANÇA''",
            "agora vá\n  eu tenho que ficar aq descançando mais uns minuti..zZzzZz",
            "zZzzZzZZZZzzzZZ\nZzzzZZZzzzzZzzzZzzz"
        ]
    
    def interact(self): return self.dialog_lines
