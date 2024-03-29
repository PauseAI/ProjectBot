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