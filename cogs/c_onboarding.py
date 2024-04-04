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
                "Newcomer Name": member.display_name,
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
            if str(emoji) in {"⛔", "🔁"}:
                # Reserved emojis
                return
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
                    "Datetime Joined": message.created_at.isoformat(),
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

    @commands.command(name="leaderboard", description="Onboarding Leaderboard")
    @admin_only()
    async def leaderboard(self, context: commands.Context):
        try:
            records = TABLES.onboarding_events.get_all()

            users_dict = {}
            for record in records:
                emoji = record["fields"].get("Emoji", "")
                if emoji in {"⛔", "🔁"}:
                    continue
                onboarder_id = record["fields"].get("Onboarder Id", "")
                if not onboarder_id:
                    continue
                if onboarder_id not in users_dict:
                    users_dict[onboarder_id] = {}
                if emoji not in users_dict[onboarder_id]:
                    users_dict[onboarder_id][emoji] = 0
                users_dict[onboarder_id][emoji] += 1
            
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
            for i, (emoji, (user_id, count)) in enumerate(sorted_rankings):
                if count <= 2:
                    continue
                user = self.bot.get_user(int(user_id))
                if not user:
                    continue
                medal = medal_emojis[i] if i < len(medal_emojis) else "🏅"
                rankings += f"{medal}  -  {emoji}{user.display_name}{emoji}  -  {count} onboardings\n"
            await context.send(rankings)
            
        except Exception as e:
            print(e, flush=True)

async def setup(bot):
    await bot.add_cog(OnboardingCog(bot))