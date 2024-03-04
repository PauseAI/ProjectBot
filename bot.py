from notion_client import Client
import yaml

with open('secrets.yml', 'r') as file:
    secrets = yaml.safe_load(file)

# Initialize the Notion client with your integration token
notion = Client(auth=secrets["notion_integration_token"])

# The ID of the database you want to retrieve properties from
database_id = secrets["notion_database_id"]

# Define the properties of the entry you want to add
# Adjust these properties to match the schema of your Notion database
entry_properties = {
    "Name": {
        "title": [
            {
                "text": {
                    "content": "Test ProjectBot",  # Example title
                },
            },
        ],
    },
    "Discord Link": {
        "url": "www.example.com",  # Example description
    },
    "Lead": {
        "select":{
                "name": "Maxime F (RationalHippy)"
            }
    },
    "Skills": {
        "multi_select": [
            {
                "name": "Think"
            },
            {
                "name": "Code"
            },
            {
                "name": "Design"
            }
        ]
    }
    # Add more properties here according to your database schema
}

# Add the entry to the database
try:
    new_entry_response = notion.pages.create(
        parent={"database_id": database_id},
        properties=entry_properties
    )
    print("New entry added to the database successfully.")
except Exception as e:
    print(f"An error occurred: {e}")