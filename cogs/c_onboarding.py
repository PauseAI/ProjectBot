from discord.ext import commands
from discord import Client
import discord
from custom_decorators import admin_only
from config import CONFIG
from airtable_client import TABLES
import datetime as dt
from messages.m_onboarding import INITIAL, MET, REPLIED, CANCEL, WEBSITE, ON_DISCORD, USER_NOT_FOUND
import re

class OnboardingCog(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            records = TABLES.onboarding_events.get_all()
            matching = [r for r in records if r["fields"].get("Newcomer Id", "") == str(member.id)]
            if matching:
                # This user has already joined in the past. We don't create a new entry
                return
            joined_at = dt.date.today().isoformat()
            if member.joined_at:
                joined_at = member.joined_at.isoformat()
            TABLES.onboarding_events.insert({
                "Newcomer Id": str(member.id),
                "Newcomer Name": member.display_name,
                "Datetime Joined": joined_at,
            }, typecast=True)
        except Exception as e:
            print(e, flush=True)

    async def onboard_discord(self, channel: discord.Thread, message: discord.Message, 
                        user: discord.User, emoji: discord.PartialEmoji):
        records = TABLES.onboarding_events.get_all()
        matching = [r for r in records if r["fields"]["Newcomer Id"] == str(message.author.id)]
        if matching:
            # This user is already in our database
            # TODO: Currently there is a timezone bug that I don't know how to fix
            TABLES.onboarding_events.update(
                matching[0]["id"],
                {
                    "Datetime Joined": message.created_at.isoformat(),
                    "Message Id": str(message.id),
                    "Onboarder Name": user.display_name,
                    "Onboarder Id": str(user.id),
                    "Datetime Onboarded": dt.datetime.now().isoformat(),
                    "Emoji": str(emoji)
                }
            )
        else:
            # This user is not in our database
            TABLES.onboarding_events.insert({
                "Datetime Joined": message.created_at.isoformat(),
                "Newcomer Name": message.author.display_name,
                "Newcomer Id": str(message.author.id),
                "Message Id": str(message.id),
                "Onboarder Name": user.display_name,
                "Onboarder Id": str(user.id),
                "Datetime Onboarded": dt.datetime.now().isoformat(),
                "Emoji": str(emoji)
            }, typecast=True)
        await user.send(INITIAL.format(
            name = message.author.display_name,
            user_id = message.author.id
            )
        )

    async def onboard_website(self, channel: discord.Thread, message: discord.Message, 
                        user: discord.User, emoji: discord.PartialEmoji):
        matches = re.findall(r"\|\|([a-zA-Z0-9]+)\|\|", message.clean_content)
        if len(matches) != 1:
            return
        record_id = matches[0]
        record = TABLES.join_pause_ai.get(record_id)
        if not record:
            await user.send(f"There seems to be an error, this person is not in our database anymore, please contact an administrator.")
        joined_discord = record["fields"].get("JoinedDiscord", "No")

        name = record["fields"].get("Name", "Anonymous")
        if joined_discord == "Yes":
            await user.send(f"{name} has indicated that they are already on Discord.")
            return
        
        TABLES.join_pause_ai.update(record_id, 
            {
                "Onboarder Name": user.display_name,
                "Onboarder Id": str(user.id),
                "Datetime Onboarded": dt.datetime.now().isoformat(),
                "Emoji": str(emoji)
            }
        )

        await user.send(WEBSITE.format(
            name=name,
            email=record["fields"].get("Email address", ""),
            country=record["fields"].get("Country", ""),
            city=record["fields"].get("City", ""),
            how_to_help=record["fields"].get("How do you want to help?", ""),
            hours_per_week=record["fields"].get("How many hours per week could you spend volunteering with PauseAI?", ""),
            types_of_action=record["fields"].get("What types of action(s) would you be interested in?", ""),
            record_id = record_id
        ))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
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
            if str(emoji) in {"⛔", "🔁"}:
                # Reserved emojis
                return
            if message.type == discord.MessageType.new_member:
                await self.onboard_discord(channel, message, user, emoji)
            else:
                await self.onboard_website(channel, message, user, emoji)
            
                
        except Exception as e:
            print(e, flush=True)

    async def undo_onboard_discord(self, message, user):
        records = TABLES.onboarding_events.get_all()
        matching = [r for r in records 
                    if r["fields"].get("Message Id", "") == str(message.id)
                    and r["fields"].get("Onboarder Id", "") == str(user.id)
                    ]
        if matching:
            TABLES.onboarding_events.update(
                matching[0]["id"],
                {
                    "Message Id": "",
                    "Onboarder Name": "",
                    "Onboarder Id": "",
                    "Datetime Onboarded": None,
                    "Emoji": ""
                }
            )
            await user.send(CANCEL.format(name=message.author.display_name))

    async def undo_onboard_website(self, message, user):
        matches = re.findall(r"\|\|([a-zA-Z0-9]+)\|\|", message.clean_content)
        if len(matches) != 1:
            return
        record_id = matches[0]
        record = TABLES.join_pause_ai.get(record_id)
        if not record:
            return
        TABLES.join_pause_ai.update(
            record_id,
            {
                "Onboarder Name": "",
                "Onboarder Id": "",
                "Datetime Onboarded": None,
                "Emoji": ""
            }
        )
        await user.send(CANCEL.format(name=message.author.display_name))

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
            if str(emoji) in {"⛔", "🔁"}:
                # Reserved emojis
                return
            if message.type == discord.MessageType.new_member:
                await self.undo_onboard_discord(message, user)
            else:
                await self.undo_onboard_website(message, user)

        except Exception as e:
            print(e, flush=True)

    @commands.command(name="onboarding", description="The onboarding pipeline")
    async def onboarding(self, context: commands.Context, stage: str, user_id: str, record_id: str = ""):
        try:
            if stage not in ["replied", "met", "discord"]:
                await context.author.send(f"Unknown onboarding stage: {stage}. The only valid options are 'replied' and 'met'")
                return
            if stage=="discord":
                # First we convert the provide alphanumeric user name into a user id
                # (unless it was already a user id)
                try:
                    user_name = self.bot.get_user(int(user_id))
                except ValueError:
                    user_name = user_id
                    user = discord.utils.get(self.bot.users, name=user_id)
                    if not user:
                        await context.author.send(USER_NOT_FOUND.format(user_name=user_name))
                        return
                    user_id = str(user.id)
                TABLES.join_pause_ai.update(record_id, {
                    "JoinedDiscord": "Yes",
                    "Discord Username": user_name,
                    "Discord Id": user_id
                    })
                await context.author.send(ON_DISCORD.format(name=user_name))
                return
            records = TABLES.onboarding_events.get_all()
            matching_user_id = [r for r in records 
                    if r["fields"].get("Newcomer Id", "") == user_id
                    ]
            if not matching_user_id:
                await context.author.send("Unable to find a newcomer with this id")
                return
            matching = [r for r in matching_user_id 
                        if r["fields"].get("Onboarder Id", "") == str(context.author.id)]
            if not matching:
                await context.author.send("You are not the onboarder for this newcomer")
                return
            # We should have identified the record (although there could still be multiple)
            record_id = matching[0]["id"]
            fields = matching[0]["fields"]
            
            if stage=="replied":
                TABLES.onboarding_events.update(record_id, {"Initial Reply": True})
                await context.author.send(REPLIED.format(name=fields["Newcomer Name"], user_id=user_id))
            elif stage=="met":
                TABLES.onboarding_events.update(record_id, {"Face Meeting": True})
                await context.author.send(MET.format(name=fields["Newcomer Name"]))
                
        except Exception as e:
            print(e, flush=True)


async def setup(bot):
    await bot.add_cog(OnboardingCog(bot))