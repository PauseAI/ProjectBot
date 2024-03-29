import discord
from notion_client import Client
from data_extraction import extract_tasks_from_description
from bot_commands import c_track, c_test
from config import secrets
import argparse

# Define the intents
intents = discord.Intents.default()  # defaults to all but the privileged ones
intents.messages = True  # to read messages
intents.guilds = True  # to access guild (server) information
intents.message_content = True  # Explicitly request permission to read message content

# Initialize the Discord client
client = discord.Client(intents=intents)

# Initialize the Notion client with your integration token
notion = Client(auth=secrets["notion_integration_token"])

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}', flush=True)

@client.event
async def on_message(message):
    try:
        # Check if the message is from you and contains the !fetch command
        print("Message received", flush=True)
        # Non-admin interactions
        if message.content.startswith('!hello'):
            await message.channel.send("Hello :)")

        # Admin interactions
        if message.author.id not in secrets["admin_user_ids"]:
            return
        
        if message.content.startswith('!track'):
            return await c_track.track(notion, message)
        
        if message.content.startswith('!test'):
            return await c_test.test(notion, message)

    except Exception as e:
        print(f"An Exception occured: {e}", flush=True)
        await message.channel.send("Ooops! Something went wrong. Try again or contact someone from @software-team.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord Bot')
    parser.add_argument('--staging', action='store_true', help='Start the bot in staging mode')
    args = parser.parse_args()
    if args.staging:
        secrets["projects_db_id"] = secrets["projects_db_id_staging"]
        secrets["tasks_db_id"] = secrets["tasks_db_id_staging"]
    client.run(secrets["discord_bot_secret"])