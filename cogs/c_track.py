from utils import ( print_message_info, 
                   get_airtable_project_properties, get_airtable_task_properties )
from data_extraction import extract_tasks_from_description
import config
from discord.ext import commands
import discord
from discord_tools import confirm_dialogue
from custom_decorators import admin_only
from airtable_client import TABLES


class TrackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="track", description="Track a project")
    @admin_only()
    async def track(self, context: commands.Context):
        try:
            if not isinstance(context.channel, discord.Thread):
                await context.response.send_message("This command is only supported in forum channels.", ephemeral=True)

            async for msg in context.channel.history(oldest_first=True, limit=1):
                print_message_info(msg)
                # Add the entry to the database
                airtable_entry = get_airtable_project_properties(msg)
                extracted_tasks = extract_tasks_from_description(msg.clean_content)
                project_record = TABLES.projects.insert(airtable_entry, typecast=True)
                print("New entry added to the database successfully.", flush=True)
                # Sending the response in the same thread
                await context.channel.send(f"Project {airtable_entry['Name']} was added to the database.")
                # Extract tasks
                if extracted_tasks is None:
                    print("Failure during tasks extraction")
                else:
                    for extracted_task in extracted_tasks:
                        task_properties_airtable = get_airtable_task_properties(extracted_task, project_record["id"])
                        skills_string = " ".join(["`"+skill+"`" for skill in extracted_task["skills"]])
                        task_string = f"{extracted_task['involvement']}: {extracted_task['task']} {skills_string}"
                        create = await confirm_dialogue(self.bot, context, "Create Task?", task_string)
                        if create:
                            TABLES.tasks.insert(task_properties_airtable, typecast=True)
                            await context.author.send("New task added to the database succesfully")
                print("Response sent succesfully", flush=True)
        except Exception as e:
            print(e, flush=True)


async def setup(bot):
    await bot.add_cog(TrackCog(bot))
