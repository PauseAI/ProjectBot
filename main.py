import argparse
import asyncio
from airtable_client import TABLES
from airtable_poller import start_pollers
from bot import start_bot
from config import CONFIG

async def main():
    await asyncio.gather(start_bot(), start_pollers())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--staging', action='store_true', help='Start the bot in staging mode')
    args = parser.parse_args()
    if args.staging:
        CONFIG.set_staging()
        TABLES.reset()
    
    asyncio.run(main())