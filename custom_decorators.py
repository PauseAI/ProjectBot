from discord.ext import commands
import config

def admin_only():
    async def predicate(ctx):
        if ctx.author.id not in config.admin_user_ids:
            await ctx.author.send("You do not have permission to use this command.")
            return False
        return True
    return commands.check(predicate)