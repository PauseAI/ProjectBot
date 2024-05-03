from airtable_poller import actions_poller
from airtable_client import TABLES
from bot import client
from messages.m_kudos import KUDO_TEMPLATES, KUDO_OTHER
from config import CONFIG

@actions_poller.on_addition
async def on_new_action(record_id: str):
    try:
        record = TABLES.actions.get(record_id)
        volunteers = TABLES.volunteers.get_all()
        kudos_channel = client.get_channel(CONFIG.kudos_channel_id)
        action_type = record["fields"].get("action_type")
        volunteer_name = record["fields"].get("volunteer_name")
        matching_volunteer = [
           r["fields"].get("Discord Id") 
           for r in volunteers 
           if r["fields"].get("Name") == volunteer_name]
        if matching_volunteer and matching_volunteer[0]:
           # We make a mention to this volunteer's Discord profile
           volunteer_name = f"<@{matching_volunteer[0]}>"
        if not volunteer_name:
            # We don't send a kudos message when there is no volunteer name
            return
        target_name = record["fields"].get("target_name")
        target_type = record["fields"].get("target_type")
        template = KUDO_TEMPLATES.get(action_type, KUDO_OTHER)
        await kudos_channel.send(template.format(
            volunteer_name=volunteer_name,
            target_name = target_name,
            target_type = target_type
        ))
    except Exception as e:
        print(e, flush=True)
