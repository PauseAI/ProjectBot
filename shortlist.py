from notion_client import Client
import yaml

with open('secrets.yml', 'r') as file:
    secrets = yaml.safe_load(file)

# Initialize the Notion client with your integration token
notion = Client(auth=secrets["notion_integration_token"])

# The ID of the database you want to retrieve properties from
PROJECTS_DATABASE_ID = secrets["notion_database_id"]
TASKS_DATABASE_ID = secrets["notion_tasks_id"]

def format_project(project):
    project_markdown = f"### {project['properties']['Discord Link']['url']}"
    #project_markdown = f"### [{project['properties']['Name']['title'][0]['plain_text']}]({project['public_url']})"
    #project_markdown = f"### #\"{project['properties']['Name']['title'][0]['plain_text']}\""

    skills = ", ".join('`' + skill["name"] + '`' for skill in project["properties"]["Skills"]["multi_select"])
    project_markdown += f" {skills}"
    project_markdown += "\n"
    #if project['properties']['Short Description']['rich_text']:  # Handle optional description
    #    project_markdown += f"{project['properties']['Short Description']['rich_text'][0]['plain_text']}\n"

    if project["properties"]["Needs Leadership"]["checkbox"]:
        project_markdown += "- 💡Needs Project Leadership💡\n"
    return project_markdown

def format_task(task):
    involvement_map = {
        "Tiny": "🟢", 
        "Medium": "🟡",
        "Big": "🔴"
        # Add more as needed
    }
    if not task["properties"]["Needs Help"]["checkbox"]:
        return ""
    involvement_symbol = involvement_map.get(task["properties"]["Involvement"]["select"]["name"], "")
    skills = ", ".join('`' + skill["name"] + '`' for skill in task["properties"]["Skills"]["multi_select"])
    spec_skills = ", ".join('`' + skill["name"] + '`' for skill in task["properties"]["Specialised Skills"]["multi_select"])
    #return f"- {involvement_symbol} {task['properties']['Involvement']['select']['name']} Task: {task['properties']['Name']['title'][0]['plain_text']} **{skills} {spec_skills}**"
    return f"- {involvement_symbol} {task['properties']['Name']['title'][0]['plain_text']} **{skills} {spec_skills}**\n"

markdown_output = """
## Biweekly Projects Shortlist
In thread is a shortlist of our most important projects, to help orient newcomers.

"""

projects_results = notion.databases.query(
    PROJECTS_DATABASE_ID,
    )

for project_row in projects_results["results"]:
    #print(project_row["properties"]["Priority"]["multi_select"][0].keys())
    if not project_row["properties"]["Priority"]["multi_select"] or not "🔥🔥🔥" in project_row["properties"]["Priority"]["multi_select"][0]["name"]:
        continue    
    project = notion.pages.retrieve(project_row['id'])
    print(project['properties']['Name']['title'][0]['plain_text'])
    markdown_output += format_project(project)

    related_tasks = notion.databases.query(
        TASKS_DATABASE_ID,
        filter={
            "property": "Projects",
            "relation": {
                "contains": project_row["id"]
            }
        }
    ) 

    for task_row in related_tasks['results']:
        task = notion.pages.retrieve(task_row['id'])
        markdown_output += format_task(task)

    markdown_output += "\n"

markdown_output += """
Legend:
🟢: Tiny Task: one off, Minimal involvement
🟡: Medium Task: Regular involvement or big one off
🔴: Big Task: Multiple hour per week
"""

with open("projects_shortlist.md", "w", encoding="utf-8") as f:
    f.write(markdown_output)
#print(markdown_output)  # You can write this to a file instead 