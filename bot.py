import discord
from discord.ext import commands
from config import CONFIG

intents = discord.Intents.default()  # defaults to all but the privileged ones
intents.messages = True  # to read messages
intents.reactions = True # to read reactions
intents.guilds = True  # to access guild (server) information
intents.members = True # to access members information
intents.message_content = True  # Explicitly request permission to read message content

# Initialize the Discord client
client = commands.Bot(intents=intents, command_prefix="!")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}', flush=True)

async def start_bot():
    async with client:
        await client.load_extension('cogs.c_track')
        await client.load_extension('cogs.c_test')
        await client.load_extension('cogs.c_list')
        await client.load_extension('cogs.c_onboarding')
        await client.load_extension('cogs.c_leaderboard')
        await client.load_extension('cogs.c_roles')
        # await client.load_extension('cogs.c_special')
        await client.start(CONFIG.discord_bot_secret)