from airtable_poller import join_poller
from airtable_client import TABLES
from bot import client
import config

@join_poller.on_addition
async def on_new_member(id: str):
    try:
        record = TABLES.join_pause_ai.get(id)
        name = record["fields"].get("Name") or "Anonymous"
        onboarding_channel = client.get_channel(config.onboarding_channel_id_staging)
        await onboarding_channel.send(f"🆕: **{name}** joined from the website! ||{id}||")
    except Exception as e:
        print(e, flush=True)