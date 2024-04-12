import argparse
import asyncio
from airtable_client import TABLES
from airtable_poller import start_pollers
from repeater import start_repeaters
from bot import start_bot
from config import CONFIG

async def main():
    await asyncio.gather(start_bot(), start_pollers(), start_repeaters())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--prod', action='store_true', help='Start the bot in production mode')
    args = parser.parse_args()
    if not args.prod:
        CONFIG.set_staging()
        TABLES.reset()
    
    asyncio.run(main())