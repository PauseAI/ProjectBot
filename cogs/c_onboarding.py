from discord.ext import commands
from custom_decorators import admin_only

class OnboardingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notion = bot.notion

    @commands.command(name="leaderboard", description="Onboarding Leaderboard")
    @admin_only()
    async def onboarding(self, context: commands.Context):
        try:
            users_dict = {}
            messages = [msg async for msg in context.channel.history(limit=1000)]
            for message in messages:
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
            await context.send(rankings)
            
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(OnboardingCog(bot))