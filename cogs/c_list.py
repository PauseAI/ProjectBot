from discord.ext import commands
from custom_decorators import admin_only
from shortlist import (LEGEND, format_project, format_task_oneline, 
                       get_all_projects, get_all_tasks)

class ListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="projects", description="Test")
    @admin_only()
    async def list_projects(self, context: commands.Context):
        try:
            projects = [p for p in get_all_projects() if p.priority==2]
            tasks = get_all_tasks()
            for project in projects:
                await context.send(format_project(project, tasks, show_description=True))
            await context.send(LEGEND)
        except Exception as e:
            print(e, flush=True)
    
    @commands.command(name="tasks", description="Test")
    @admin_only()
    async def list_tasks(self, context: commands.Context):
        try:
            projects = get_all_projects()
            tasks = [t for t in get_all_tasks() if t.involvement=="Tiny" and t.needs_help]
            for i in range(len(tasks)//5):
                text = ""
                for task in tasks[i*5:(i+1)*5]:
                    text += format_task_oneline(task, projects)
                await context.send(text)
        except Exception as e:
            print(e, flush=True)


async def setup(bot):
    await bot.add_cog(ListCog(bot))