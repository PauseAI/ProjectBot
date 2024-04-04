from discord.ext import commands
from discord import Client
import discord
from custom_decorators import admin_only
import config
from airtable_client import TABLES
import datetime as dt

class OnboardingCog(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        print("NEWCOMER!", flush=True)
        try:
            records = TABLES.onboarding_events.get_all()
            matching = [r for r in records if r["fields"].get("Newcomer Id", "") == str(member.id)]
            if matching:
                # This user has already joined in the past. We don't create a new entry
                return
            TABLES.onboarding_events.insert({
                "Newcomer Id": member.id,
                "Newcomer Name": member.name,
                "Datetime Joined": member.created_at.isoformat()
            }, typecast=True)
        except Exception as e:
            print(e, flush=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
            if channel.id != config.onboarding_channel_id:
                return
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.new_member:
                return
            # A reaction has been added on a new member message
            user = await self.bot.fetch_user(payload.user_id)
            emoji = payload.emoji
            records = TABLES.onboarding_events.get_all()
            matching = [r for r in records if r["fields"]["Newcomer Id"] == str(message.author.id)]
            if matching:
                # This user is already in our database
                # TODO: Currently there is a timezone bug that I don't know how to fix
                TABLES.onboarding_events.update(
                    matching[0]["id"],
                    {
                        "Datetime Joined": message.created_at.isoformat(),
                        "Message Id": str(payload.message_id),
                        "Onboarder Name": user.display_name,
                        "Onboarder Id": str(user.id),
                        "Datetime Onboarded": dt.datetime.now().isoformat(),
                        "Emoji": str(emoji)
                    }
                )
            else:
                # This user is not in our database
                TABLES.onboarding_events.insert({
                    "Newcomer Name": message.author.display_name,
                    "Newcomer Id": str(message.author.id),
                    "Message Id": str(payload.message_id),
                    "Onboarder Name": user.display_name,
                    "Onboarder Id": str(user.id),
                    "Datetime Onboarded": dt.datetime.now().isoformat(),
                    "Emoji": str(emoji)
                }, typecast=True)
            await user.send((
                f"Thank you so much for Onboarding {message.author.display_name}!\n" +
                f"Let me know how it goes! If they reply to your initial message, please send me the following:\n"
                f"!onboarding replied {message.author.id}"
                ))
        except Exception as e:
            print(e, flush=True)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        try:
            channel = await self.bot.fetch_channel(payload.channel_id)
            if channel.id != config.onboarding_channel_id:
                return
            message = await channel.fetch_message(payload.message_id)
            if message.type != discord.MessageType.new_member:
                return
            # A reaction has been removed on a new member message
            user = await self.bot.fetch_user(payload.user_id)
            records = TABLES.onboarding_events.get_all()
            matching = [r for r in records 
                        if r["fields"].get("Message Id", "") == str(payload.message_id)
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
                await user.send(
                    f"You are no longer onboarding {message.author.display_name}. If that was a mistake, you can add your reaction again."
                )

        except Exception as e:
            print(e, flush=True)

    @commands.command(name="onboarding", description="The onboarding pipeline")
    async def onboarding(self, context: commands.Context, stage: str, user_id: str):
        try:
            if stage not in ["replied", "met"]:
                await context.author.send(f"Unknown onboarding stage: {stage}. The only valid options are 'replied' and 'met'")
                return
            records = TABLES.onboarding_events.get_all()
            matching_user_id = [r for r in records 
                    if r["fields"].get("Newcomer Id", "") == user_id
                    ]
            if not matching_user_id:
                await context.author.send("Unable to find a newcomer with this id")
                return
            matching = [r for r in records 
                        if r["fields"].get("Onboarder Id", "") == str(context.author.id)]
            if not matching:
                await context.author.send("You are not the onboarder for this newcomer")
                return
            # We should have identified the record (although there could still be multiple)
            record_id = matching[0]["id"]
            fields = matching[0]["fields"]
            
            if stage=="replied":
                TABLES.onboarding_events.update(record_id, {"Initial Reply": True})
                await context.author.send(
                    f"Thank you so much for letting me know that {fields['Newcomer Name']} has " +
                    f"replied to you! If you are able to have a face to face conversation with them, " +
                    f"please send me the following message: \n"+
                    f"!onboarding met {user_id}"
                    )
            elif stage=="met":
                TABLES.onboarding_events.update(record_id, {"Face Meeting": True})
                await context.author.send(
                    f"Thank you so much for letting me know that you have now met {fields['Newcomer Name']}! " +
                    f"You Rock!"
                    )
                
        except Exception as e:
            print(e, flush=True)

    @commands.command(name="populate", description="The onboarding pipeline")
    @admin_only()
    async def populate(self, context: commands.Context):
        try:
            channel = await self.bot.fetch_channel(config.onboarding_channel_id)
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

    @commands.command(name="leaderboard", description="Onboarding Leaderboard")
    @admin_only()
    async def leaderboard(self, context: commands.Context):
        try:
            users_dict = {}
            channel = self.bot.get_channel(config.onboarding_channel_id)
            messages = [msg async for msg in channel.history(limit=1000)]
            i = 0
            for message in messages:
                if i%50 == 0:
                    await context.author.send(f"Processed {i} messages")
                i+=1
                if message.type.name != "new_member" or len(message.reactions) != 1:
                    continue
                reaction = message.reactions[0]
                async for user in reaction.users():
                    if user.display_name not in users_dict:
                        users_dict[user.display_name] = {}
                    if str(reaction.emoji) not in users_dict[user.display_name]:
                        users_dict[user.display_name][str(reaction.emoji)] = 0
                    users_dict[user.display_name][str(reaction.emoji)] += 1
            
            # Create the emoji rankings
            emoji_dict = {}
            for user, emojis in users_dict.items():
                for emoji, count in emojis.items():
                    if emoji not in emoji_dict:
                        emoji_dict[emoji] = (user, count)
                    else:
                        current_user, current_count = emoji_dict[emoji]
                        if count > current_count:
                            emoji_dict[emoji] = (user, count)
            
            # Sort the emoji rankings based on count in descending order
            sorted_rankings = sorted(emoji_dict.items(), key=lambda x: x[1][1], reverse=True)

            # Send the emoji rankings
            rankings = "Emoji Rankings:\n"
            medal_emojis = ["🥇", "🥈", "🥉"]
            for i, (emoji, (user, count)) in enumerate(sorted_rankings):
                if count <= 2:
                    continue
                medal = medal_emojis[i] if i < len(medal_emojis) else "🏅"
                rankings += f"{medal} {emoji}: {user} - {count} times\n"
            await channel.send(rankings)
            
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(OnboardingCog(bot))