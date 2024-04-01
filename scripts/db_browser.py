from notion_client import Client
import yaml

with open('secrets.yml', 'r') as file:
    secrets = yaml.safe_load(file)

# Initialize the Notion client with your integration token
notion = Client(auth=secrets["notion_integration_token"])

# The ID of the database you want to retrieve properties from
database_id = secrets["notion_database_id"]

try:
    # Retrieve the database details
    database_details = notion.databases.retrieve(database_id=database_id)

    # Print each property name and its type
    print("Properties in the database:")
    for property_name, property_details in database_details["properties"].items():
        print(f"- {property_name}: {property_details['type']}")
except Exception as e:
    print(f"Failed to retrieve database properties: {e}")
