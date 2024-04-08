from airtable_poller import join_poller
from airtable_client import TABLES
from bot import client
from messages.m_onboarding import NEW_SIGNUP
import config

@join_poller.on_addition
async def on_new_member(record_id: str):
    try:
        record = TABLES.join_pause_ai.get(record_id)
        onboarding_channel = client.get_channel(config.onboarding_channel_id)
        await onboarding_channel.send(NEW_SIGNUP.format(
            name=record["fields"].get("Name", "Anonymous"),
            country=record["fields"].get("Country", "?"),
            how_to_help=record["fields"].get("How do you want to help?", ""),
            record_id=record_id
        ))
    except Exception as e:
        print(e, flush=True)
