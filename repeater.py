import asyncio
from config import CONFIG
from typing import Callable

REPEATERS = []

class Repeater:
    """Runs tasks repeatedly at some time interval"""
    def __init__(self, config_name: str):
        self.config_name=config_name
        self.tasks = []

    async def start(self):
        print(f"Repeater starting. Interval: {CONFIG.get(self.config_name)}", flush=True)
        while True:
            for task in self.tasks:
                await task()
            await asyncio.sleep(CONFIG.get(self.config_name))

    def register(self, func: Callable[[], None]):
        self.tasks.append(func)
        return func

async def start_repeaters():
    from repeat_tasks import r_user_ids  # noqa: F401 -- this is needed to start the async repeater
    await asyncio.gather(*[repeater.start() for repeater in REPEATERS])

slow_repeater = Repeater("slow_repeat_interval")
REPEATERS.append(slow_repeater)