
import pygame as PYG
import os

from src.Config import IMAGES_DIR

def load_tile(filename: str, size: tuple[int, int] = (32, 32)) -> PYG.Surface:
    path = os.path.join(IMAGES_DIR, filename)
    try:
        image = PYG.image.load(path).convert_alpha()
        return PYG.transform.scale(image, size)
    except FileNotFoundError:
        surf = PYG.Surface(size)
        surf.fill((225, 0, 255))
        return surf