import discord
from notion_client import Client
import yaml
from data_extraction import extract_tasks_from_description

with open('secrets.yml', 'r') as file:
    secrets = yaml.safe_load(file)

# Define the intents
intents = discord.Intents.default()  # defaults to all but the privileged ones
intents.messages = True  # to read messages
intents.guilds = True  # to access guild (server) information
intents.message_content = True  # Explicitly request permission to read message content

# Initialize the Discord client
client = discord.Client(intents=intents)

# Initialize the Notion client with your integration token
notion = Client(auth=secrets["notion_integration_token"])

# The ID of the database you want to retrieve properties from
database_id = secrets["notion_database_id"]

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}', flush=True)

@client.event
async def on_message(message):
    # Check if the message is from you and contains the !fetch command
    print("Message received", flush=True)
    if message.content.startswith('!track') and message.author.id == secrets["user_id"]:
        if isinstance(message.channel, discord.Thread):
            thread = message.channel
            async for msg in thread.history(oldest_first=True, limit=1):
                thread_url = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}"
                print(f"Title: {msg.channel.name}")
                #print(f"Original Post Content: {msg.clean_content}")
                #print(f"Author: {msg.author.display_name}")
                print(f"Tags:")
                for tag in msg.channel.applied_tags:
                    print(f"    - {tag.name}")
                print(f"URL: {thread_url}")
                # Add the entry to the database
                entry_properties = properties_from_message(msg)
                page_content = page_content_from_msg(msg)
                extracted_tasks = extract_tasks_from_description(msg.clean_content)
                try:
                    notion_response = notion.pages.create(
                        parent={"database_id": database_id},
                        properties=entry_properties,
                        children=page_content
                    )
                    print("New entry added to the database successfully.", flush=True)
                    if extracted_tasks is None:
                        print("Failure during tasks extraction")
                    else:
                        for extracted_task in extracted_tasks:
                            task_properties = get_task_properties(extracted_task, notion_response["id"])
                            print("Task: ", extracted_task["task"])
                            x = input("Create? [y/n]")
                            if x=="y":
                                notion.pages.create(
                                    parent={"database_id": secrets["notion_tasks_id"]},
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
                except Exception as e:
                    print(f"An error occurred: {e}", flush=True)
        else:
            await message.channel.send("This command is only supported in forum channels.")

def get_task_properties(task, project_id):
    properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": task["task"]
                    }
                }
            ]
        },
        "Skills": {
            "multi_select": [{"name": skill} for skill in task["skills"]]
        },
        "Involvement": {
            "select": {
                "name": task["involvement"]
            }
        },
        "Projects": {
            "relation": [
                {
                    "id": project_id
                }
            ]
        }
    }
    return properties

def properties_from_message(msg):
    thread_url = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}"
    entry_properties = {
        "Name": {
            "title": [
                {
                    "text": {
                        "content": msg.channel.name
                    }
                }
            ]
        },
        "Discord Link": {
            "url": thread_url
        },  
        "Lead": {
            "select": {
                "name": msg.author.display_name
            }
        },
        "Skills": {
            "multi_select": [{"name": tag.name} for tag in msg.channel.applied_tags]
        }
    }
    return entry_properties

def page_content_from_msg(msg):
    page_content = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": msg.clean_content,
                        },
                    },
                ],
            },
        },
        # You can add more blocks here as needed
    ]
    return page_content

client.run(secrets["discord_bot_secret"])