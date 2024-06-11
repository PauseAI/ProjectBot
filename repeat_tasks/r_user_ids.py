from repeater import slow_repeater
from airtable_client import TABLES
import discord
from bot import client

@slow_repeater.register
async def resolve_user_ids():
    """On the forms, people sign up with their discord user name, but this is not
    an identifier. This task derives the user id from the user name and populates
    the relevant tables"""
    try:
        for table in [TABLES.members, TABLES.volunteers]:
            records = table.get_all()
            for record in records:
                user_name = record["fields"].get("discord_username")
                user_id = record["fields"].get("discord_id")
                if user_name and not user_id:
                    user = discord.utils.get(client.users, name=user_name.lower())
                    if user:
                        table.update(record["id"], {
                            "discord_username": user_name.lower(),
                            "discord_id": str(user.id)})
                        continue
                    # This was not the username, let's try the display name
                    user = discord.utils.get(client.users, display_name=user_name)
                    if user:
                        table.update(record["id"], {"discord_id": str(user.id)})
                        continue
                if user_id and not user_name:
                    try:
                        user = client.get_user(int(user_id))
                        if user:
                            table.update(record["id"], {"discord_username": user.name})
                    except ValueError:
                        pass
    except Exception as e:
        print(e, flush=True)