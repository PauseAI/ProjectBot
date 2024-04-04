from utils import ( print_message_info, extract_channel_id,
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

    @commands.command(name="update", description="Update project")
    async def update(self, context: commands.Context, discord_url=None):
        try:
            print("Update command", flush=True)
            if not discord_url:
                await context.author.send("You need to pass the link to the project thread in the command (!test <link>)")
                return
            channel_id = extract_channel_id(discord_url)
            if not channel_id:
                await context.author.send("This channel url is not well formed")
                return
            # We were able to extract a channel id from this url
            records = TABLES.projects.get_all()
            matching = [r for r in records if r["fields"].get("Discord Link", "") == discord_url]
            if not matching:
                await context.author.send("This project is not in the database. Use !track instead")
                return
            if len(matching) > 1:
                await context.author.send("This project is duplicated in the database. Please investigate.")
                return
            # Now we have exactly one match
            project_id = matching[0]["id"]
            old_data = matching[0]["fields"]
            try:
                channel = self.bot.get_channel(channel_id)
            except:
                await context.author.send("Unable to retrieve this channel")
                return
            if not channel:
                await context.author.send("Unable to retrieve this channel")
                return
            async for msg in channel.history(oldest_first=True, limit=1):
                new_data = get_airtable_project_properties(msg)
                for field in ["Name", "Description", "Lead", "Skills"]:
                    if str(new_data[field]).strip() != str(old_data[field]).strip():
                        if await confirm_dialogue(self.bot, context, f"Update {field}?", 
                            f"Old: {old_data[field][:300]}\n New: {new_data[field][:300]}"
                            ):
                            TABLES.projects.update(project_id, {field: new_data[field]}, typecast=True)
                            await context.author.send("Done")
                await context.author.send("Update finished")

        except Exception as e:
            await context.author.send("Something unexpected happened, please contact an administrator.")
            print(e, flush=True)

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
