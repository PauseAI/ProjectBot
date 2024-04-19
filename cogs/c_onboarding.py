from discord.ext import commands
from discord import Client
import discord
import traceback
from config import CONFIG
from airtable_client import TABLES
from messages.m_onboarding import REMINDER
from cogs.onboarding import (find_user_name_id, format_message_discord, 
                             get_pai_member, insert_newcomer, record_id_from_message)
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
            insert_newcomer(member)
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
                params["db_id"] = f"o-{record_id}"
                params["table_id"] = "o"
                if not record_id:
                    # this user was not in the database, we add them
                    record_id = insert_newcomer(message.author)
                print("Processing reaction to new_member")
                record = TABLES.onboarding_events.get(record_id)
                await ONBOARDING_MANAGER.reaction_trigger(user, message, emoji, record, TABLES.onboarding_events, params)
            else:
                record_id = record_id_from_message(message)
                params["db_id"] = f"j-{record_id}"
                params["table_id"] = "j"
                if record_id is None:
                    return
                print("Processing reaction to website sign up")
                record = TABLES.join_pause_ai.get(record_id)
                if not record:
                    await user.send(f"There seems to be an error, this person is not in our database anymore, please contact an administrator.")
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
                params["db_id"] = f"o-{record_id}"
                params["table_id"] = "o"
                if not record_id:
                    # this user was not in the database, we add them
                    record_id = insert_newcomer(message.author)
                print("Processing clear reaction to new_member")
                record = TABLES.onboarding_events.get(record_id)
                await ONBOARDING_MANAGER.clear_reaction_trigger(user, message, emoji, record, TABLES.onboarding_events, params)
            else:
                record_id = record_id_from_message(message)
                params["db_id"] = f"j-{record_id}"
                params["table_id"] = "j"
                if record_id is None:
                    return
                print("Processing clear reaction to website sign up")
                record = TABLES.join_pause_ai.get(record_id)
                if not record:
                    await user.send(f"There seems to be an error, this person is not in our database anymore, please contact an administrator.")
                await ONBOARDING_MANAGER.clear_reaction_trigger(user, message, emoji, record, TABLES.join_pause_ai, params)

        except Exception as e:
            print(traceback.format_exc(), flush=True)

    @commands.command(name="research", description="Logging research about a user")
    async def research(self, context: commands.Context, subcommand: str, db_id: str, *, text: str):
        try:
            print(f"Command research {subcommand}")
            table_id, record_id = db_id.split("-")
            if table_id == "j":
                table = TABLES.join_pause_ai
            elif table_id == "o":
                table = TABLES.onboarding_events
            else:
                await context.author.send("PLACEHOLDER invalid identifier")
            record = table.get(record_id)
            if not record:
                await context.author.send("PLACEHOLDER error user not found")

            # TODO: Gathering all the data we have?
            # Eventually, grabbing both records if the tables are linked together
            params = {"text": text, "db_id": db_id, "table_id": table_id}
            await ONBOARDING_MANAGER.command_trigger("research", subcommand, context.author, None, record, table, params)
        except Exception:
            print(traceback.format_exc(), flush=True)

    @commands.command(name="onboarding", description="The onboarding pipeline")
    async def onboarding(self, context: commands.Context, subcommand: str, db_id: str, user_name_or_id: str = None):
        try:
            print(f"Command onboarding {subcommand}")
            table_id, record_id = db_id.split("-")
            if table_id == "j":
                table = TABLES.join_pause_ai
            elif table_id == "o":
                table = TABLES.onboarding_events
            else:
                await context.author.send("PLACEHOLDER invalid identifier")
            record = table.get(record_id)
            if not record:
                await context.author.send("PLACEHOLDER error user not found")

            if user_name_or_id is not None:
                user_name, user_id = find_user_name_id(self.bot, user_name_or_id)
            else:
                user_name, user_id = None, None

            # TODO: Gathering all the data we have?
            # Eventually, grabbing both records if the tables are linked together
            params = {"db_id": db_id, "user_name": user_name, "user_id": user_id, "table_id": table_id}
            await ONBOARDING_MANAGER.command_trigger("onboarding", subcommand, context.author, None, record, table, params)

        except Exception as e:
            print(traceback.format_exc(), flush=True)

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