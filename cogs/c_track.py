from utils import ( get_notion_project_properties, page_content_from_msg, 
                   get_notion_task_properties, print_message_info, 
                   get_airtable_project_properties, get_airtable_task_properties )
from data_extraction import extract_tasks_from_description
import config
from discord.ext import commands
import discord
from discord_tools import confirm_dialogue
from custom_decorators import admin_only


class TrackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion = bot.notion

    @commands.command(name="track", description="Track a project")
    @admin_only()
    async def track(self, context: commands.Context):
        try:
            if not isinstance(context.channel, discord.Thread):
                await context.response.send_message("This command is only supported in forum channels.", ephemeral=True)

            async for msg in context.channel.history(oldest_first=True, limit=1):
                print_message_info(msg)
                # Add the entry to the database
                #thread_url = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}"
                entry_properties = get_notion_project_properties(msg)
                airtable_entry = get_airtable_project_properties(msg)
                page_content = page_content_from_msg(msg)
                extracted_tasks = extract_tasks_from_description(msg.clean_content)
                notion_response = self.notion.pages.create(
                    parent={"database_id": config.projects_db_id},
                    properties=entry_properties,
                    children=page_content
                )
                project_record = self.bot.projects_table.insert(airtable_entry, typecast=True)
                print("New entry added to the database successfully.", flush=True)
                # Constructing the response message
                response_message = (
                    f"Project Tracker: {notion_response['public_url']}"
                )
                # Sending the response in the same thread
                await context.channel.send(response_message)
                # Extract tasks
                if extracted_tasks is None:
                    print("Failure during tasks extraction")
                else:
                    for extracted_task in extracted_tasks:
                        task_properties = get_notion_task_properties(extracted_task, notion_response["id"])
                        task_properties_airtable = get_airtable_task_properties(extracted_task, project_record["id"])
                        skills_string = " ".join(["`"+skill+"`" for skill in extracted_task["skills"]])
                        task_string = f"{extracted_task['involvement']}: {extracted_task['task']} {skills_string}"
                        create = await confirm_dialogue(self.bot, context, "Create Task?", task_string)
                        if create:
                            self.notion.pages.create(
                                parent={"database_id": config.tasks_db_id},
                                properties=task_properties
                            )
                            self.bot.tasks_table.insert(task_properties_airtable, typecast=True)
                            await context.author.send("New task added to the database succesfully")
                print("Response sent succesfully", flush=True)
        except Exception as e:
            print(e, flush=True)


async def setup(bot):
    await bot.add_cog(TrackCog(bot))
