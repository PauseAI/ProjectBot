from discord.ext import commands
from discord import Client
import discord
from custom_decorators import admin_only
from config import CONFIG
from airtable_client import TABLES
import datetime as dt

class SpecialCog(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    @commands.command(name="populate", description="The onboarding pipeline")
    @admin_only()
    async def populate(self, context: commands.Context):
        try:
            channel = await self.bot.fetch_channel(CONFIG.onboarding_channel_id)
            messages = [
                msg async for msg in channel.history(limit=1000)
                if msg.type==discord.MessageType.new_member
                ]
            message_id_to_record_id = {}
            deleted_records = set()
            for message in messages:
                record = TABLES.onboarding_events.insert(
                    {
                        "Newcomer Id": str(message.author.id),
                        "Newcomer Name": message.author.display_name,
                        "Datetime Joined": message.created_at.isoformat()
                    }
                )
                message_id_to_record_id[message.id] = record["id"]
            # cleaning duplicates
            records = TABLES.onboarding_events.get_all()
            join_times = [
                (r["fields"]["Newcomer Id"], r["fields"]["Datetime Joined"]) for r in records
            ]
            minimal_join_times = {}
            format_str = '%Y-%m-%dT%H:%M:%S.%fZ'
            for i, dtj in join_times:
                if i not in minimal_join_times:
                    minimal_join_times[i] = dtj
                else:
                    if dt.datetime.strptime(dtj, format_str) < dt.datetime.strptime(minimal_join_times[i], format_str):
                        minimal_join_times[i] = dtj
            for r in records:
                if r["fields"]["Datetime Joined"] != minimal_join_times[r["fields"]["Newcomer Id"]]:
                    TABLES.onboarding_events.delete(r["id"])
                    deleted_records.add(r["id"])

            for message in messages:
                if message_id_to_record_id[message.id] in deleted_records:
                    continue
                if len(message.reactions) != 1:
                    continue
                reaction = message.reactions[0]
                async for user in reaction.users():
                    TABLES.onboarding_events.update(
                        message_id_to_record_id[message.id],
                        {
                            "Message Id": str(message.id),
                            "Onboarder Id": str(user.id),
                            "Onboarder Name": str(user.name),
                            "Emoji": str(reaction.emoji)
                        }
                    )

        except Exception as e:
            print(e, flush=True)