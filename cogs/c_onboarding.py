from discord.ext import commands
from discord import Client
import discord
import traceback
from cogs.onboarding_config import VERSION
from config import CONFIG
from airtable_client import TABLES
from messages.m_onboarding import REMINDER
from cogs.onboarding import (find_user_name_id, format_message_discord, 
                             get_pai_member, insert_newcomer, record_id_from_message,
                             table_id_and_record_id_from_db_id, user_id_from_user_name)
from cogs.onboarding_manager import ONBOARDING_MANAGER


class OnboardingCog(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            if get_pai_member(member):
                # already a member
                return
            insert_newcomer(member, pipeline_version=VERSION)
        except Exception as e:
            print(e, flush=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print("Reaction Add", flush=True)
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
            if channel.id != CONFIG.onboarding_channel_id:
                return
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.new_member and not message.content.startswith("🆕:"):
                return
            # A reaction has been added on a new member message (from discord or website)
            user = await self.bot.fetch_user(payload.user_id)
            
            emoji = str(payload.emoji)
           
            params = {}

            if message.type == discord.MessageType.new_member:
                record_id = get_pai_member(message.author)
                params["db_id"] = message.author.name
                params["table_id"] = TABLES.onboarding_events.table_name
                if not record_id:
                    # this user was not in the database, we add them
                    record_id = insert_newcomer(message.author, pipeline_version=VERSION)
                print("Processing reaction to new_member")
                record = TABLES.onboarding_events.get(record_id)
                await ONBOARDING_MANAGER.reaction_trigger(user, message, emoji, record, TABLES.onboarding_events, params)
            else:
                record_id = record_id_from_message(message)
                if record_id is None:
                    # Somebody has reacted to a regular message
                    return
                record = TABLES.join_pause_ai.get(record_id)
                if not record:
                    await user.send(f"There seems to be an error, this person is not in our database anymore, please contact an administrator.")
                email = record["fields"].get("Email address")
                if email is None:
                    # That's problematic, every record in this table should have an email address
                    await user.send("Error: this user has not filled in his email address")
                    return
                params["db_id"] = email
                params["table_id"] = TABLES.join_pause_ai.table_name
                if record["fields"].get("pipeline_version", "") == "":
                    # There is no pipeline version attached to this person, we update that
                    TABLES.join_pause_ai.update(record_id, {"pipeline_version": VERSION})
                print("Processing reaction to website sign up")
                await ONBOARDING_MANAGER.reaction_trigger(user, message, emoji, record, TABLES.join_pause_ai, params)
          
        except Exception as e:
            print(traceback.format_exc(), flush=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        try:
            print("Reaction Remove")
            channel = await self.bot.fetch_channel(payload.channel_id)
            if channel.id != CONFIG.onboarding_channel_id:
                return
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.new_member and not message.content.startswith("🆕:"):
                return
            # A reaction has been removed on a new member message (from discord or website)
            user = await self.bot.fetch_user(payload.user_id)
            emoji = str(payload.emoji)

            params = {}
            
            if message.type == discord.MessageType.new_member:
                record_id = get_pai_member(message.author)
                params["db_id"] = message.author.name
                params["table_id"] = TABLES.onboarding_events.table_name
                if not record_id:
                    # this user was not in the database, we add them
                    record_id = insert_newcomer(message.author)
                print("Processing clear reaction to new_member")
                record = TABLES.onboarding_events.get(record_id)
                await ONBOARDING_MANAGER.clear_reaction_trigger(user, message, emoji, record, TABLES.onboarding_events, params)
            else:
                record_id = record_id_from_message(message)
                if record_id is None:
                    # Somebody has reacted to a regular message
                    return
                record = TABLES.join_pause_ai.get(record_id)
                if not record:
                    await user.send(f"There seems to be an error, this person is not in our database anymore, please contact an administrator.")
                email = record["fields"].get("Email address")
                if email is None:
                    # That's problematic, every record in this table should have an email address
                    await user.send("Error: this user has not filled in his email address")
                    return
                params["db_id"] = email
                params["table_id"] = TABLES.join_pause_ai.table_name
                await ONBOARDING_MANAGER.clear_reaction_trigger(user, message, emoji, record, TABLES.join_pause_ai, params)

        except Exception as e:
            print(traceback.format_exc(), flush=True)


    @commands.command(name="research", description="Logging research about a user")
    async def research(self, context: commands.Context, subcommand: str, db_id: str, *, text: str):
        try:
            print(f"Command research {subcommand}")
            table_id, record_id = table_id_and_record_id_from_db_id(self.bot, db_id)
            user_name = None
            user_id = None
            user = None
            if table_id == TABLES.join_pause_ai.table_name:
                table = TABLES.join_pause_ai
            elif table_id == TABLES.onboarding_events.table_name:
                table = TABLES.onboarding_events
                user_name = db_id
                user_id = user_id_from_user_name(self.bot, db_id)
                user = self.bot.get_user(int(user_id))
            else:
                await context.author.send("Error: the user identifier that you have provided does not match our records.")
                return
            record = table.get(record_id)
            if not record:
                # there is a real problem there
                await context.author.send("Error: we could not find this user in our database. Contact an administrator")
                return

            # TODO: Gathering all the data we have?
            # Eventually, grabbing both records if the tables are linked together
            params = {"text": text, "db_id": db_id, "table_id": table_id, "user_name": user_name, "user_id": user_id}
            await ONBOARDING_MANAGER.command_trigger("research", subcommand, context.author, user, record, table, params)
        except Exception:
            print(traceback.format_exc(), flush=True)

    @commands.command(name="onboarding", description="The onboarding pipeline")
    async def onboarding(self, context: commands.Context, subcommand: str, db_id: str, user_name: str = None):
        """
        Use this command to move a user to the next stage of the pipeline.
        The available subcommands are:
        - replied
        - met
        - checkin
        - email 
        """
        try:
            print(f"Command onboarding {subcommand}")
            table_id, record_id = table_id_and_record_id_from_db_id(self.bot, db_id)
            provided_user_id = None
            provided_user_name = None
            provided_user_display_name = None
            if user_name is not None:
                """
                if table_id != TABLES.join_pause_ai.table_name:
                    await context.author.send("Error: A username should only be passed for a website signup")
                    return
                """
                provided_user_id = user_id_from_user_name(self.bot, user_name)
                if provided_user_id is None:
                    context.author.send("Error: the user_name you have provided does not exist")
                    return
                provided_user_name = user_name
                provided_user = self.bot.get_user(int(provided_user_id))
                provided_user_display_name = provided_user.display_name
            user_id = None
            user = None
            user_name = None
            if table_id == TABLES.join_pause_ai.table_name:
                table = TABLES.join_pause_ai
            elif table_id == TABLES.onboarding_events.table_name:
                table = TABLES.onboarding_events
                user_name = db_id
                user_id = user_id_from_user_name(self.bot, db_id)
                user = self.bot.get_user(int(user_id))
            else:
                await context.author.send("Error: the user identifier that you have provided does not match our records.")
                return
            record = table.get(record_id)
            if not record:
                # there is a real problem there
                await context.author.send("Error: we could not find this user in our database. Contact an administrator")
                return

            # TODO: Gathering all the data we have?
            # Eventually, grabbing both records if the tables are linked together
            params = {"db_id": db_id, "user_name": user_name, "user_id": user_id, "table_id": table_id,
                      "provided_user_name": provided_user_name, "provided_user_id": provided_user_id, 
                      "provided_user_display_name": provided_user_display_name}
            await ONBOARDING_MANAGER.command_trigger("onboarding", subcommand, context.author, user, record, table, params)

        except Exception as e:
            print(traceback.format_exc(), flush=True)

    @commands.command(name="version")
    async def version(self, context: commands.Context):
        """Returns the current version of the onboarding pipeline"""
        await context.author.send(VERSION)

    @commands.command(name="onboardinglist", description="List of people I am onboarding")
    async def onboardinglist(self, context: commands.Context):
        records = TABLES.onboarding_events.get_all()
        matching = [r for r in records 
                    if r["fields"].get("Onboarder Id") == str(context.author.id)]
        if not matching:
            await context.author.send("It looks like you are not onboarding anyone at the moment")
            return
        
        messages = []
        for record in matching:
            if record["fields"].get("Face Meeting"):
                messages.append(f"- **{record['fields'].get('Newcomer Name')}**: DONE")
                continue
            stage = "met" if record["fields"].get("Initial Reply") else "replied"
            messages.append(format_message_discord(REMINDER, record, stage=stage))
        
        for i in range(len(messages)//5+1):
            await context.author.send("\n".join(messages[i*5:(i+1)*5]))

async def setup(bot):
    await bot.add_cog(OnboardingCog(bot))