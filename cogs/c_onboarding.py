from discord.ext import commands
from discord import Client
import discord
import traceback
from config import CONFIG
from airtable_client import TABLES
from messages.m_onboarding import (
    INITIAL, MET, REPLIED, CANCEL, WEBSITE, ON_DISCORD, USER_NOT_FOUND,
    REMINDER)
from cogs.onboarding import (find_user_name_id, format_message_discord, get_pai_member, get_pai_member_user_id, get_researcher, has_researcher, insert_newcomer, update_joined_discord, update_onboarder, 
                        update_joined, record_id_from_message, format_message_website,
                        get_onboarder, erase_onboarder, update_researcher)
from cogs.onboarding_manager import ONBOARDING_MANAGER

_ONBOARD_PIPELINE = [
    {
        "name": "replied",
        "message": REPLIED,
        "checkbox": "Initial Reply"
    },
    {
        "name": "met",
        "message": MET,
        "checkbox": "Face Meeting"
    }
]

RESERVED_EMOJIS = {"⛔", "🔁", "🧵", "🚩"}

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

    async def start_research_discord(self, message: discord.Message,
                                     user: discord.User):
        record_id = get_pai_member(message.author)
        if not record_id:
            # this user was not in the database, we add them
            record_id = insert_newcomer(message.author)
        # then we update the onboarding
        update_joined(record_id, message)
        if has_researcher(TABLES.onboarding_events, record_id):
            await user.send("PLACEHOLDER Already has researcher")
            return
        update_researcher(TABLES.onboarding_events, record_id, user)
        await user.send("PLACEHOLDER Researching")

    async def end_research_discord(self, message: discord.Message,
                                     user: discord.User, is_vip: bool):
        record_id = get_pai_member(message.author)
        if not record_id:
            # this user was not in the database, we add them
            record_id = insert_newcomer(message.author)
        if get_researcher(TABLES.onboarding_events, record_id) != str(user.id):
            await user.send("PLACEHOLDER You are not the researcher")
            return
        if not TABLES.onboarding_events.get(record_id)["fields"].get("Research Result"):
            await user.send("PLACEHOLDER log research result first")
            return
        TABLES.onboarding_events.update(record_id, {
            "Researched": True,
            "Is VIP": is_vip
        })
        await user.send("PLACEHOLDER Researched")

    async def onboard_discord(self, message: discord.Message, 
                        user: discord.User, emoji: discord.PartialEmoji):
        record_id = get_pai_member(message.author)
        if not record_id:
            # this user was not in the database, we add them
            record_id = insert_newcomer(message.author)
        # then we update the onboarding
        update_joined(record_id, message)
        update_onboarder(TABLES.onboarding_events, record_id, user, emoji)
        await user.send(INITIAL.format(
            name = message.author.display_name,
            user_id = message.author.id
            )
        )

    async def onboard_website(self, message: discord.Message, 
                        user: discord.User, emoji: discord.PartialEmoji):
        record_id = record_id_from_message(message)
        if record_id is None:
            return
        record = TABLES.join_pause_ai.get(record_id)
        if not record:
            await user.send(f"There seems to be an error, this person is not in our database anymore, please contact an administrator.")
        if record["fields"].get("JoinedDiscord", "No") == "Yes":
            await user.send(format_message_website(
                "{name} has indicated that they are already on Discord. Their username is {user_name}",
                record
            ))
            return
        if not record["fields"].get("Researched"):
            await user.send(format_message_website(
                "{name} has not been researched yet",
                record
            ))
            return
        
        update_onboarder(TABLES.join_pause_ai, record_id, user, emoji)
        await user.send(format_message_website(WEBSITE, record))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print("ADDING", flush=True)
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
            if channel.id != CONFIG.onboarding_channel_id:
                return
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.new_member and not message.content.startswith("🆕:"):
                return
            # A reaction has been added on a new member message (from discord or website)
            user = await self.bot.fetch_user(payload.user_id)
            emoji = payload.emoji
            if str(emoji) in RESERVED_EMOJIS:
                # Reserved emojis
                return
            if message.type == discord.MessageType.new_member:
                if str(emoji) == "🔍":
                    await self.start_research_discord(message, user)
                elif str(emoji) == "🥇":
                    await self.end_research_discord(message, user, True)
                elif str(emoji) == "🥈":
                    await self.end_research_discord(message, user, False)
                else:
                    await self.onboard_discord(message, user, emoji)
            else:
                if str(emoji) == "🔍":
                    pass
                elif str(emoji) == "🥇":
                    pass
                elif str(emoji) == "🥈":
                    pass
                else:
                    await self.onboard_website(message, user, emoji)
            
                
        except Exception as e:
            print(traceback.format_exc(), flush=True)

    async def undo_onboard_discord(self, message, user):
        record_id = get_onboarder(message, user)
        if record_id:
            erase_onboarder(TABLES.onboarding_events, record_id)
            await user.send(CANCEL.format(name=message.author.display_name))

    async def undo_onboard_website(self, message, user):
        record_id = record_id_from_message(message)
        if record_id is None:
            return
        record = TABLES.join_pause_ai.get(record_id)
        if not record:
            return
        erase_onboarder(TABLES.join_pause_ai, record_id)
        await user.send(format_message_website(CANCEL, record))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
            if channel.id != CONFIG.onboarding_channel_id:
                return
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.new_member and not message.content.startswith("🆕:"):
                return
            # A reaction has been removed on a new member message (from discord or website)
            user = await self.bot.fetch_user(payload.user_id)
            emoji = payload.emoji
            if str(emoji) in RESERVED_EMOJIS:
                # Reserved emojis
                return
            if message.type == discord.MessageType.new_member:
                await self.undo_onboard_discord(message, user)
            else:
                await self.undo_onboard_website(message, user)

        except Exception as e:
            print(traceback.format_exc(), flush=True)

    @commands.command(name="research", description="Logging research about a user")
    async def research(self, context: commands.Context, user_id: str, *, text: str):
        record_id = get_pai_member_user_id(user_id)
        if not record_id:
            await context.author.send("PLACEHOLDER error user not found")
        if get_researcher(TABLES.onboarding_events, record_id) != str(context.author.id):
            await context.author.send("PLACEHOLDER You are not the researcher")
            return
        TABLES.onboarding_events.update(record_id, {
            "Research Result": text,
        })
        await context.author.send(f"PLACEHOLDER Thanks for logging research now use emoji")

    @commands.command(name="onboarding", description="The onboarding pipeline")
    async def onboarding(self, context: commands.Context, stage: str, user: str, record_id: str = ""):
        try:
            if stage not in ["replied", "met", "discord"]:
                await context.author.send(f"Unknown onboarding stage: {stage}. The only valid options are 'replied' and 'met'")
                return
            if stage=="discord":
                # First we convert the provide alphanumeric user name into a user id
                # (unless it was already a user id)
                user_name, user_id = find_user_name_id(self.bot, user)
                if not user_id:
                    await context.author.send(USER_NOT_FOUND.format(user_name=user))
                    return
                update_joined_discord(record_id, user_name, user_id)
                await context.author.send(ON_DISCORD.format(name=user_name))
                return
            
            record = TABLES.onboarding_events.match("Newcomer Id", user)
            if not record:
                await context.author.send("Unable to find a newcomer with this id")
                return
            if record["fields"].get("Onboarder Id", "") != str(context.author.id):
                await context.author.send("You are not the onboarder for this newcomer")
                return
            # We should have identified the record (although there could still be multiple)
            record_id = record["id"]
            fields = record["fields"]
            
            for pipeline_stage in _ONBOARD_PIPELINE:
                if stage == pipeline_stage["name"]:
                    TABLES.onboarding_events.update(record_id, {pipeline_stage["checkbox"]: True})
                    await context.author.send(pipeline_stage["message"].format(name=fields["Newcomer Name"], user_id=user))
                    return
                
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