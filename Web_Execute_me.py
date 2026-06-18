
import asyncio
import exe

try:
    asyncio.get_running_loop()
    asyncio.create_task(exe.Launcher.run())
    asyncio.ensure_future(exe.Launcher.run())
except RuntimeError as E: asyncio.run(exe.Launcher.run())
