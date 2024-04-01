import csv
from airtable import Airtable
import config

# Airtable API configuration
airtable_base_id = config.airtable_base_id
airtable_api_key = config.airtable_token
projects_table_name = 'Projects'
tasks_table_name = 'Tasks'

# Initialize Airtable clients
projects_table = Airtable(airtable_base_id, projects_table_name, api_key=airtable_api_key)
tasks_table = Airtable(airtable_base_id, tasks_table_name, api_key=airtable_api_key)

# Read tasks data from the CSV file
tasks_data = []
with open('tasks.csv', 'r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    for row in reader:
        tasks_data.append(row)

# Fetch project records from Airtable
projects = projects_table.get_all()

# Create a mapping of project names to their record IDs
project_map = {project['fields']['Name']: project['id'] for project in projects}
help_mapping = {"No": False, "Yes": True}


# Iterate over tasks data and create records in Airtable
for task in tasks_data:
    project_name = task['Projects'].split(" (https://")[0]
    project_id = project_map.get(project_name)
    print(task)
    if project_id:
        # Create the task record with the linked project
        fields = {
            'Name': task['Name'],
            'Description': task['Description'],
            'Involvement': task['Involvement'],
            'Needs Help': help_mapping.get(task['Needs Help']),
            'Projects': [project_id],
            'Skills': task['Skills'].split(", "),
            'Specialised Skills': task['Specialised Skills'].split(", "),
            'Status': task['Status'],
            'Volunteers': task['Volunteers'].split(", "),
        }
        tasks_table.insert(fields, typecast=True)
        print(f"Task created: {task['Name']}")
    else:
        print(f"Project not found for task: {task['Name']}")