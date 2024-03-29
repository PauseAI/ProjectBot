from utils import properties_from_message, page_content_from_msg, get_task_properties, print_message_info
from data_extraction import extract_tasks_from_description
from config import secrets
import discord


async def track(notion, message):
    if not isinstance(message.channel, discord.Thread):
        await message.channel.send("This command is only supported in forum channels.")

    thread = message.channel
    async for msg in thread.history(oldest_first=True, limit=1):
        print_message_info(msg)
        # Add the entry to the database
        thread_url = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}"
        entry_properties = properties_from_message(msg)
        page_content = page_content_from_msg(msg)
        extracted_tasks = extract_tasks_from_description(msg.clean_content)
        notion_response = notion.pages.create(
            parent={"database_id": secrets["projects_db_id"]},
            properties=entry_properties,
            children=page_content
        )
        print("New entry added to the database successfully.", flush=True)
        # Extract tasks
        if extracted_tasks is None:
            print("Failure during tasks extraction")
        else:
            for extracted_task in extracted_tasks:
                task_properties = get_task_properties(extracted_task, notion_response["id"])
                print("Task: ", extracted_task["task"])
                x = input("Create? [y/n]")
                if x=="y":
                    notion.pages.create(
                        parent={"database_id": secrets["tasks_db_id"]},
                        properties=task_properties
                    )
                    print("New task added to the database succesfully")

        # Constructing the response message
        response_message = (
            f"Project Tracker: {notion_response['public_url']}"
        )
        # Sending the response in the same thread
        await message.channel.send(response_message)
        print("Response sent succesfully", flush=True)

        
