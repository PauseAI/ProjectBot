from discord.ext import commands
from typing import Tuple
from discord_tools import confirm_dialogue

def get_user_info_str(context: commands.Context) -> str:
    usr = context.author
    return ( f"Display Name: {usr.display_name}\n" +
             f"Name: {usr.name}\n" +
             f"Global Name: {usr.global_name}\n" +
             f"ID: {usr.id}" )

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion = bot.notion

    @commands.command(name="test", description="Test")
    async def test(self, context: commands.Context):
        await context.send(get_user_info_str(context))
        create = await confirm_dialogue(self.bot, context, "Create Task?", "This is the task text `write` `research`", "blah")
        if create:
            await context.author.send("YEEES")
        else:
            await context.author.send("NOOOOAA")

async def setup(bot):
    await bot.add_cog(TestCog(bot))