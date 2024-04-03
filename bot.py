import discord
from discord.ext import commands
from airtable_client import TABLES
import config
import argparse
import asyncio

# Define the intents
intents = discord.Intents.default()  # defaults to all but the privileged ones
intents.messages = True  # to read messages
intents.reactions = True # to read reactions
intents.guilds = True  # to access guild (server) information
intents.message_content = True  # Explicitly request permission to read message content

# Initialize the Discord client
#client = discord.Client(intents=intents)
client = commands.Bot(intents=intents, command_prefix="!")


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}', flush=True)


@client.event
async def on_interaction(interaction):
    pass

async def main():
    async with client:
        await client.load_extension('cogs.c_track')
        await client.load_extension('cogs.c_test')
        await client.load_extension('cogs.c_list')
        await client.load_extension('cogs.c_onboarding')
        await client.start(config.discord_bot_secret)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--staging', action='store_true', help='Start the bot in staging mode')
    args = parser.parse_args()
    if args.staging:
        config.airtable_base_id = config.airtable_base_id_staging
        config.discord_bot_secret = config.discord_bot_secret_staging
        TABLES.set_staging()
    
    asyncio.run(main())