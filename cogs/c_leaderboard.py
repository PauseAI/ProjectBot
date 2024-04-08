from discord.ext import commands
from airtable_client import TABLES

class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard", description="Onboarding Leaderboard")
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
    await bot.add_cog(LeaderboardCog(bot))