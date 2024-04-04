def get_airtable_project_properties(msg):
    thread_url = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}"
    entry_properties = {
        "Name": msg.channel.name,
        "Discord Link": thread_url,
        "Lead": msg.author.display_name,
        "Skills": [tag.name for tag in msg.channel.applied_tags],
        "Description": msg.clean_content,
    }
    return entry_properties

def get_airtable_task_properties(task, project_id):
    properties = {
        "Name": task["task"],
        "Skills": task["skills"],
        "Involvement": task["involvement"],
        "Projects": [project_id]
    }
    return properties

def print_message_info(msg):
    print("Message info: ", flush=True)
    try:
        print(f"Title: {msg.channel.name}", flush=True)
        #print(f"Original Post Content: {msg.clean_content}")
        #print(f"Author: {msg.author.display_name}")
        print(f"Tags:", flush=True)
        for tag in msg.channel.applied_tags:
            print(f"    - {tag.name}", flush=True)
    except Exception as e:
        print(f"Could not print message info. Exception: {e}", flush=True)

def extract_channel_id(channel_url: str):
    if not channel_url.startswith("https://discord.com/channels/"):
        return None
    ids = channel_url.strip("https://discord.com/channels/").split("/")
    if not len(ids) == 2:
        return None
    try:
        return int(ids[1])
    except ValueError:
        return None