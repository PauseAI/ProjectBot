import asyncio
from typing import Callable, List
from airtable_client import TABLES
from config import CONFIG

POLLERS = []

class AirtablePoller:
    def __init__(self, table_name: str, config_name: str):
        self.config_name = config_name
        self.table_name = table_name
        self.current_ids = set()
        self.listeners_add = []
        self.listeners_delete = []
        self.started = False

    async def start(self):
        print(f"{self.table_name} poller starting. Interval: {CONFIG.get(self.config_name)}", flush=True)
        while True:
            table = TABLES.get_table(self.table_name)
            records = table.get_all(fields=[])
            new_ids = set([r["id"] for r in records])
            if self.started:
                added = new_ids - self.current_ids
                deleted = self.current_ids - new_ids
            else:
                added, deleted = set(), set()
                self.started = True
            
            if added:
                await self._notify_listeners(self.listeners_add, list(added))
            
            if deleted:
                await self._notify_listeners(self.listeners_delete, list(deleted))
            
            self.current_ids = new_ids
            await asyncio.sleep(CONFIG.get(self.config_name))

    async def _notify_listeners(self, listeners, ids):
        for listener in listeners:
            for id in ids:
                await listener(id)

    def on_addition(self, func: Callable[[str], None]):
        """
        Decorator to register a listener for added records.
        """
        self.listeners_add.append(func)
        return func

    def on_deletion(self, func: Callable[[str], None]):
        """
        Decorator to register a listener for deleted records.
        """
        self.listeners_delete.append(func)
        return func

async def start_pollers():
    from polling_actions import p_new_member
    await asyncio.gather(*[p.start() for p in POLLERS])

join_poller = AirtablePoller("Join Pause AI", config_name="polling_interval")
POLLERS.append(join_poller)