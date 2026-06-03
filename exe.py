
import sys, os
import asyncio

if getattr(sys, 'frozen', False): BASE_DIR = sys._MEIPASS
else: BASE_DIR = os.path.dirname(os.path.abspath(os.getcwd()))

sys.path.insert(0, BASE_DIR)

class Launcher():
    async def run():
        from src.core.Core import Core
        game = Core()
        await game.run()

if __name__ == "__main__": 
    try:
        asyncio.get_running_loop()
        asyncio.create_task(Launcher.run())
    except RuntimeError: asyncio.run(Launcher.run())
