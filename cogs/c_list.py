from discord.ext import commands
from discord_tools import confirm_dialogue
from custom_decorators import admin_only
from shortlist import get_markdown

class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="projects", description="Test")
    @admin_only()
    async def list_projects(self, context: commands.Context):
        try:
            markdown_projects, _ = get_markdown()
            await context.send(markdown_projects)
        except Exception as e:
            print(e, flush=True)
    
    @commands.command(name="tasks", description="Test")
    @admin_only()
    async def list_tasks(self, context: commands.Context):
        try:
            _, markdown_tasks = get_markdown()
            await context.send(markdown_tasks)
        except Exception as e:
            print(e, flush=True)


async def setup(bot):
    await bot.add_cog(ListCog(bot))