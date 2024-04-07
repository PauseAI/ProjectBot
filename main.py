import argparse
import asyncio
from airtable_client import TABLES
from airtable_poller import start_pollers
from bot import start_bot
import config

async def main():
    await asyncio.gather(start_bot(), start_pollers())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--staging', action='store_true', help='Start the bot in staging mode')
    args = parser.parse_args()
    if args.staging:
        config.airtable_base_id = config.airtable_base_id_staging
        config.discord_bot_secret = config.discord_bot_secret_staging
        config.onboarding_channel_id = config.onboarding_channel_id_staging
        TABLES.set_staging()
    
    asyncio.run(main())