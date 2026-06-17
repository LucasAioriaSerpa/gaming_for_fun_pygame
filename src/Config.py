
from collections import namedtuple as nTuple
import sys, os

_OS_PATH = os.path

if getattr(sys, 'frozen', False): ROOT_DIR = sys._MEIPASS
else: ROOT_DIR = _OS_PATH.dirname(_OS_PATH.dirname(_OS_PATH.abspath(__file__)))

DATA_DIR = _OS_PATH.join(ROOT_DIR, "data")
CONTENT_DIR = _OS_PATH.join(ROOT_DIR, "content")

SIZE = nTuple("SIZE", "WIDTH HEIGHT")

WINDOW_TITLE  = "The Fall"
SCREEN_SIZE   = SIZE(1280, 720)
SCREEN_ZOOM   = (2, 4)
FPS           = 60
RESIZABLE     = False

COLOR = nTuple("COLOR", "R G B")

class Colors:
    BLACK       : type[tuple] = COLOR(  0,   0,   0)
    WHITE       : type[tuple] = COLOR(255, 255, 255)
    BG          : type[tuple] = COLOR( 15,  12,  25)
    ACCENT      : type[tuple] = COLOR(120,  80, 220)
    ACCENT2     : type[tuple] = COLOR( 60, 200, 160)
    TEXT        : type[tuple] = COLOR(220, 215, 235)
    TEXT_DIM    : type[tuple] = COLOR(110, 105, 130)
    
    FOX_TIP     : type[tuple] = COLOR(214, 200, 252)
    FOX_BASE    : type[tuple] = COLOR(250, 151, 109)
    FOX_PURPLE  : type[tuple] = COLOR(179, 102, 246)
    FOX_RED_ORG : type[tuple] = COLOR(216,  73,  59)
    FOX_MAGENTA : type[tuple] = COLOR(176,   1,  73)
    FOX_OUTLINE : type[tuple] = COLOR(101,   6,  14)

class GameState:
    START_SCREEN = "start_screen"
    PLAYING      = "playing"
    PAUSED       = "paused"
    GAME_OVER    = "game_over"
    CUTSCENE     = "cutscene"
    CREDITS      = "credits"

FONT_SIZE_TITLE  = 72
FONT_SIZE_LARGE  = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL  = 20
