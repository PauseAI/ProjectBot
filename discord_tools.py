import discord
from discord.ext import commands
import random
import asyncio

async def confirm_dialogue(bot, context: commands.Context, title: str, description: str) -> bool:
    id = str(random.randint(0, 100000))
    embed = discord.Embed(title=title, description=description)
    yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green, custom_id=f"yes_{id}")
    no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.gray, custom_id=f"no_{id}")
    view = discord.ui.View()
    view.add_item(yes_button)
    view.add_item(no_button)
    await context.author.send(embed=embed, view=view)
    def check(interaction: discord.Interaction):
        return interaction.user == context.author and interaction.channel.type == discord.ChannelType.private
    try:
        interaction = await bot.wait_for('interaction', check=check, timeout=60.0)
        await interaction.response.defer()
        if interaction.data["custom_id"] == f"yes_{id}":
            return True
        elif interaction.data["custom_id"] == f"no_{id}":
            return False
    except asyncio.TimeoutError:
        # User didn't respond within the timeout period
        await context.author.send("The tracking menu has timed out. Please try again.")
        return None