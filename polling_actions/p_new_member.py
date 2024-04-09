from airtable_poller import join_poller
from airtable_client import TABLES
from bot import client
from messages.m_onboarding import NEW_SIGNUP
from config import CONFIG

@join_poller.on_addition
async def on_new_member(record_id: str):
    try:
        record = TABLES.join_pause_ai.get(record_id)
        onboarding_channel = client.get_channel(CONFIG.onboarding_channel_id)
        how_to_help = record["fields"].get("How do you want to help?", "")
        how_to_help_truncated = how_to_help[:300]
        if len(how_to_help) > len(how_to_help_truncated):
            how_to_help_truncated += "..."
        await onboarding_channel.send(NEW_SIGNUP.format(
            name=record["fields"].get("Name", "Anonymous"),
            country=record["fields"].get("Country", "?"),
            how_to_help=how_to_help_truncated,
            record_id=record_id
        ))
    except Exception as e:
        print(e, flush=True)
