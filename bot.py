import discord
from discord.ext import commands
from notion_client import Client
from airtable import Airtable
from data_extraction import extract_tasks_from_description
import config
import argparse
import asyncio

# Define the intents
intents = discord.Intents.default()  # defaults to all but the privileged ones
intents.messages = True  # to read messages
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
        await client.start(config.discord_bot_secret)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--staging', action='store_true', help='Start the bot in staging mode')
    args = parser.parse_args()
    if args.staging:
        config.projects_db_id = config.projects_db_id_staging
        config.tasks_db_id = config.tasks_db_id_staging
        config.airtable_base_id = config.airtable_base_id_staging
        config.discord_bot_secret = config.discord_bot_secret_staging
    
    # Initialize the Notion client with your integration token
    client.notion = Client(auth=config.notion_integration_token)
    client.projects_table = Airtable(config.airtable_base_id, config.projects_table_name, api_key=config.airtable_token)
    client.tasks_table = Airtable(config.airtable_base_id, config.tasks_table_name, api_key=config.airtable_token)

    asyncio.run(main())