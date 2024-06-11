import traceback
from discord.ext import commands
from discord import Client
import discord

from airtable_client import TABLES

class RolesCog(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot

    #@commands.command("assign_team")
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        We check if user roles have changed. If a team role was added or removed,
        we update the database accordingly
        """
        try:
            if len(before.roles) < len(after.roles):
                # added a role
                team_records = TABLES.teams.get_all()
                team_roles = {
                    r["fields"].get("discord_role"): r["id"] 
                    for r in team_records
                    }
                new_role = next(role for role in after.roles if role not in before.roles)
                if new_role.name in team_roles.keys():
                    print(f"Role {new_role.name} added to {after.name}")
                    volunteer_record = TABLES.volunteers.match("discord_id", str(after.id))
                    if volunteer_record:
                        TABLES.volunteers.update(volunteer_record["id"],
                            {
                                "member_of": volunteer_record["fields"].get("member_of", []) + [team_roles[new_role.name]]
                            }
                        )
            elif len(before.roles) > len(after.roles):
                # removed a role
                team_records = TABLES.teams.get_all()
                team_roles = {
                    r["fields"].get("discord_role"): r["id"] 
                    for r in team_records
                    }
                old_role = next(role for role in before.roles if role not in after.roles) 
                if old_role.name in team_roles.keys():
                    print(f"Role {old_role.name} removed to {after.name}")
                    volunteer_record = TABLES.volunteers.match("discord_id", str(after.id))
                    if volunteer_record:
                        prev_roles = volunteer_record["fields"].get("member_of", [])
                        new_roles = [r for r in prev_roles if r != team_roles[old_role.name]]
                        TABLES.volunteers.update(volunteer_record["id"],
                            {
                                "member_of": new_roles
                            }
                        )
        except Exception:
            print(traceback.format_exc())

async def setup(bot):
    await bot.add_cog(RolesCog(bot))