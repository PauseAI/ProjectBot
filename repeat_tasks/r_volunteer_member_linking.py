from repeater import slow_repeater
from airtable_client import TABLES
import discord
from bot import client

@slow_repeater.register
async def volunteer_member_linking():
    """This task links the volunteers table with the members table, 
    using the email address as the identifier field.
    """
    try:
        records_volunteers = TABLES.volunteers.get_all()
        records_members = TABLES.members.get_all()
        for record_v in records_volunteers:
            if record_v["fields"].get("member"):
                # This one is already linked, we skip it
                continue
            email_address = record_v["fields"].get("email_address")
            if not email_address:
                continue
            matching_m = [r for r in records_members 
                if r["fields"].get("Email address")==email_address]
            if matching_m:
                record_id_m = matching_m[0]["id"]
                TABLES.volunteers.update(record_v["id"], {"member": [record_id_m]})
    except Exception as e:
        print(e, flush=True)