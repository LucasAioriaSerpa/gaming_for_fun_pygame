import sys, os
import asyncio

if getattr(sys, 'frozen', False): BASE_DIR = sys._MEIPASS
else: BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

async def run():
    from src.core.Core import Core
    game = Core()
    await game.run()

asyncio.run(run())
