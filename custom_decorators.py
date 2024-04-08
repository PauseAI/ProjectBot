from discord.ext import commands
from config import CONFIG

def admin_only():
    async def predicate(ctx):
        if ctx.author.id not in CONFIG.admin_user_ids:
            await ctx.author.send("You do not have permission to use this command.")
            return False
        return True
    return commands.check(predicate)