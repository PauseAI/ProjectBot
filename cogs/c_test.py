from discord.ext import commands
import discord

def get_user_info_str(context: commands.Context) -> str:
    usr = context.author
    return ( f"Display Name: {usr.display_name}\n" +
             f"Name: {usr.name}\n" +
             f"Global Name: {usr.global_name}\n" +
             f"ID: {usr.id}" )

class TestCog(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.command(name="test", description="Test")
    async def test(self, context: commands.Context, test_arg="blah"):
        await context.send(get_user_info_str(context))
        await context.send(test_arg)
        
        emoji_dict = {}
        async for message in context.channel.history(limit=None):
            for reaction in message.reactions:
                if str(reaction.emoji) not in emoji_dict:
                    emoji_dict[str(reaction.emoji)] = 0
                emoji_dict[str(reaction.emoji)] += 1
        await context.send(str(emoji_dict))

async def setup(bot):
    await bot.add_cog(TestCog(bot))