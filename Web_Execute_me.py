
import asyncio

import exe

try:
    asyncio.get_running_loop()
    asyncio.create_task(exe.Launcher.run())
except RuntimeError: asyncio.run(exe.Launcher.run())
