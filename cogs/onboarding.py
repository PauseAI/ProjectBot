from airtable_client import TABLES
import datetime as dt
from airtable import Airtable
import discord
import re
from typing import Dict, Tuple

def get_pai_member(member: discord.Member) -> str:
    """
    Returns the record id if member is found or None
    """
    records = TABLES.onboarding_events.get_all()
    matching = [r for r in records if r["fields"].get("Newcomer Id", "") == str(member.id)]
    if matching:
        return matching[0]["id"]

def get_onboarder(message: discord.Message, user: discord.User):
    """
    Returns the record id if the pair (onboarder, message) is found or None
    """
    records = TABLES.onboarding_events.get_all()
    matching = [r for r in records 
                if r["fields"].get("Message Id", "") == str(message.id)
                and r["fields"].get("Onboarder Id", "") == str(user.id)
                ]
    if matching:
        return matching[0]["id"]

def insert_newcomer(member: discord.Member) -> str:
    """
    Returns record id
    """
    joined_at = dt.date.today().isoformat()
    if member.joined_at:
        joined_at = member.joined_at.isoformat()
    record = TABLES.onboarding_events.insert({
        "Newcomer Id": str(member.id),
        "Newcomer Name": member.display_name,
        "Datetime Joined": joined_at,
    }, typecast=True)
    return record["id"]

def update_joined(record_id: str, message: discord.Message):
    TABLES.onboarding_events.update(
        record_id,
        {
            "Datetime Joined": message.created_at.isoformat(),
            "Message Id": str(message.id),
        }
    )

def update_joined_discord(record_id: str, user_name: str, user_id: str):
    TABLES.join_pause_ai.update(record_id, {
        "JoinedDiscord": "Yes",
        "Discord Username": user_name,
        "Discord Id": user_id
        })

def find_user_name_id(bot: discord.Client, user_name_or_id: str) -> Tuple[str, str]:
    """
    Returns a pair (user_name, user_id) or (None, None) if it was not found
    """
    try:
        user_id = user_name_or_id
        user_name = bot.get_user(int(user_id))
        return user_name, user_id
    except ValueError:
        user_name = user_name_or_id
        user = discord.utils.get(bot.users, name=user_name)
        if user:
            return user_name, str(user.id)
    return None, None

def update_onboarder(table: Airtable, record_id: str, user: discord.User, emoji: str):
    table.update(record_id, {
        "Onboarder Name": user.display_name,
        "Onboarder Id": str(user.id),
        "Datetime Onboarded": dt.datetime.now().isoformat(),
        "Emoji": str(emoji)
    })

def erase_onboarder(table: Airtable, record_id: str):
    table.update(
        record_id,
        {
            "Onboarder Name": "",
            "Onboarder Id": "",
            "Datetime Onboarded": None,
            "Emoji": ""
        }
    )

def record_id_from_message(message: discord.Message) -> str:
    matches = re.findall(r"\|\|([a-zA-Z0-9]+)\|\|", message.clean_content)
    if len(matches) != 1:
        return
    return matches[0]

def format_message_website(message: str, record: Dict, **kwargs) -> str:
    return message.format(
        name=record["fields"].get("Name", "Anonymous"),
        user_name=record["fields"].get("Discord Username", "not mentioned"),
        email=record["fields"].get("Email address", ""),
        country=record["fields"].get("Country", ""),
        city=record["fields"].get("City", ""),
        how_to_help=record["fields"].get("How do you want to help?", ""),
        hours_per_week=record["fields"].get("How many hours per week could you spend volunteering with PauseAI?", ""),
        types_of_action=record["fields"].get("What types of action(s) would you be interested in?", ""),
        record_id = record["id"],
        joined_discord = record["fields"].get("JoinedDiscord", "No"),
        **kwargs
    )

def format_message_discord(message: str, record: Dict, **kwargs) -> str:
    return message.format(
        name=record["fields"].get("Newcomer Name"),
        user_id=record["fields"].get("Newcomer Id"),
        **kwargs
    )