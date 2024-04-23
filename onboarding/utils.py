from airtable_client import TABLES
import datetime as dt
from airtable import Airtable
import discord
import re
from typing import Dict, Tuple

def get_pai_member_user_id(user_id: str) -> str:
    record = TABLES.onboarding_events.match("Newcomer Id", user_id)
    if record:
        return record["id"]

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

def insert_newcomer(member: discord.Member, pipeline_version: str) -> str:
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
        "pipeline_version": pipeline_version,
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
    
def table_id_and_record_id_from_db_id(bot: discord.Client, db_id: str) -> Tuple[str, str]:
    """db_id can be a discord username or an email. Returns (None, None) if not found"""
    user_id = user_id_from_user_name(bot, db_id)
    if user_id:
        table_id = TABLES.onboarding_events.table_name
        all_records = TABLES.onboarding_events.get_all()
        matching = [r for r in all_records if r["fields"].get("Newcomer Id") == user_id]
        if len(matching) == 0:
            # could not find them in our database
            return None, None
        if  len(matching) > 1:
            # There could be duplicates in the database. We remove the ones that have been aborted
            # Note that there can stil be duplicates after this... For now we will return the first one
            # TODO: better handling of this problem
            matching = [r for r in matching if r["fields"].get("Aborted", False) == False]
        record_id = matching[0]["id"]
        return table_id, record_id
    record = record_from_email(db_id)
    if record is not None:
        table_id = TABLES.join_pause_ai.table_name
        return table_id, record["id"]
    return None, None

def record_from_email(email: str):
    record = TABLES.join_pause_ai.match("Email address", email)
    return record
    
def user_id_from_user_name(bot: discord.Client, user_name: str) -> str:
    """Returns None if can't be found"""
    user = discord.utils.get(bot.users, name=user_name)
    if user:
        return str(user.id)

def find_user_name_id(bot: discord.Client, user_name_or_id: str) -> Tuple[str, str]:
    """
    Returns a pair (user_name, user_id) or (None, None) if it was not found
    """
    try:
        user_id = user_name_or_id
        user_name = bot.get_user(int(user_id))
        return user_name, user_id
    except ValueError:
        user_id = user_id_from_user_name(bot, user_name_or_id)
        if user_id:
            return user_name_or_id, user_id
    return None, None

def update_onboarder(table: Airtable, record_id: str, user: discord.User, emoji: str):
    table.update(record_id, {
        "Onboarder Name": user.display_name,
        "Onboarder Id": str(user.id),
        "Datetime Onboarded": dt.datetime.now().isoformat(),
        "Emoji": str(emoji)
    })

def update_researcher(table: Airtable, record_id: str, user: discord.User):
    table.update(record_id, {
        "Researcher Name": user.display_name,
        "Researcher Id": str(user.id),
        "Datetime Researched": dt.datetime.now().isoformat(),
    })

def has_researcher(table: Airtable, record_id: str) -> bool:
    return table.get(record_id)["fields"].get("Researcher Id", "") != ""

def get_researcher(table: Airtable, record_id: str) -> bool:
    return table.get(record_id)["fields"].get("Researcher Id", "")

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

def reset_researcher(table: Airtable, record_id: str):
    table.update(
        record_id,
        {
            "Researcher Name": "",
            "Researcher Id": "",
            "Datetime Researched": None,
        }
    )

def reset_onboarder(table: Airtable, record_id: str):
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