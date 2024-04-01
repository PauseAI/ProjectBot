import discord
import yaml

with open('secrets.yml', 'r') as file:
    secrets = yaml.safe_load(file)

BOT_TOKEN = secrets["discord_bot_secret"]
CHANNEL_ID = 1174807044990193775 # 1100491867675709580
EMOJI = '👍' 

# Define the intents
intents = discord.Intents.default()  # defaults to all but the privileged ones
intents.messages = True  # to read messages
intents.guilds = True  # to access guild (server) information
intents.message_content = True  # Explicitly request permission to read message content

# Initialize the Discord client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})', flush=True)
    print('------')

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f'Channel with ID {CHANNEL_ID} not found.', flush=True)
        return

    async for message in channel.history(limit=1000):  # Fetch unlimited history
        for reaction in message.reactions:
            if str(reaction.emoji) == EMOJI:
                count = reaction.count
                print(f'Message ID {message.id} has {count} {EMOJI} reactions', flush=True)

client.run(BOT_TOKEN)