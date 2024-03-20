from notion_client import Client
import yaml
from dataclasses import dataclass
from typing import List

@dataclass
class Project:
    id: str
    name: str
    discord_url: str
    public_url: str
    description: str = None # Optional property
    skills: list[str] = None
    priority: int = 0
    needs_leadership: bool = False
    tasks: list[str] = None

@dataclass
class Task:
    id: str
    name: str
    involvement: str
    needs_help: bool
    skills: list[str] = None
    special_skills: list[str] = None
    projects: list[str] = None

with open('secrets.yml', 'r') as file:
    secrets = yaml.safe_load(file)

# Initialize the Notion client with your integration token
notion = Client(auth=secrets["notion_integration_token"])

# The ID of the database you want to retrieve properties from
PROJECTS_DATABASE_ID = secrets["notion_database_id"]
TASKS_DATABASE_ID = secrets["notion_tasks_id"]
DESCRIPTION = True

def get_project(project) -> Project:
    return Project(
        id = project["id"],
        name=project['properties']['Name']['title'][0]['plain_text'],
        discord_url=project['properties']['Discord Link']['url'],
        public_url=project['public_url'],
        description=project['properties']['Short Description']['rich_text'][0]['plain_text'] if project['properties']['Short Description']['rich_text'] else "",
        skills=[skill["name"] for skill in project["properties"]["Skills"]["multi_select"]],
        priority={"": -1, "🔥": 0, "🔥🔥": 1, "🔥🔥🔥": 2}[project["properties"]["Priority"]["multi_select"][0]["name"] if project["properties"]["Priority"]["multi_select"] else ""],
        needs_leadership=project["properties"]["Needs Leadership"]["checkbox"],
        tasks=[rel["id"] for rel in project["properties"]["Tasks"]["relation"]]
    )

def get_task(task) -> Task:
    return Task(
        id = task["id"],
        name=task['properties']['Name']['title'][0]['plain_text'],
        involvement=task["properties"]["Involvement"]["select"]["name"] if task["properties"]["Involvement"]["select"] else "",
        needs_help = task["properties"]["Needs Help"]["checkbox"],
        skills=[skill["name"] for skill in task["properties"]["Skills"]["multi_select"]],
        special_skills=[skill["name"] for skill in task["properties"]["Specialised Skills"]["multi_select"]],
        projects=[rel["id"] for rel in task["properties"]["Projects"]["relation"]],
        )

def format_project(project: Project):
    project_markdown = f"### {project.discord_url}"
    #project_markdown = f"### [{project.name}]({project.public_url})"

    skills = ", ".join('`' + skill + '`' for skill in task.skills)
    project_markdown += f" {skills}"
    project_markdown += "\n"
    if DESCRIPTION and project.description:  # Handle optional description
        project_markdown += project.description+"\n"

    if project.needs_leadership:
        project_markdown += "- 💡Needs Project Leadership💡\n"
    return project_markdown

def format_task(task: Task):
    involvement_map = {
        "Tiny": "🟢", 
        "Medium": "🟡",
        "Big": "🔴"
        # Add more as needed
    }
    if not task.needs_help:
        return ""
    involvement_symbol = involvement_map.get(task.involvement, "")
    skills = ", ".join('`' + skill + '`' for skill in task.skills)
    spec_skills = ", ".join('`' + skill + '`' for skill in task.special_skills)
    return f"- {involvement_symbol} {task.name} **{skills} {spec_skills}**\n"

def format_tiny_task(task: Task, projects: List[Project]):
    if not task.needs_help or not task.involvement == "Tiny":
        return ""
    project = [p for p in projects if p.id == task.projects[0]][0]
    skills = ", ".join('`' + skill + '`' for skill in task.skills)
    spec_skills = ", ".join('`' + skill + '`' for skill in task.special_skills)
    return f"- {project.discord_url} {task.name} **{skills} {spec_skills}**\n"

markdown_output = """
## Biweekly Projects Shortlist
In thread is a shortlist of our most important projects, to help orient newcomers.
"""

markdown_tiny_tasks = """
## Biweekly Tiny Tasks Shortlist
In thread is a list of tiny tasks that most people should be able to contribute to immediately
"""

print("Grabbing Projects...")
projects_results = notion.databases.query(
    PROJECTS_DATABASE_ID,
    )
projects = [get_project(project_row) for project_row in projects_results["results"]]

print("Grabbing tasks...")
tasks_results = notion.databases.query(
    TASKS_DATABASE_ID
)
tasks = [get_task(task_row) for task_row in tasks_results["results"]]

for task in tasks:
    markdown_tiny_tasks += format_tiny_task(task, projects)

for project in projects:
    if project.priority < 2: 
        continue    
    print(project.name)
    markdown_output += format_project(project)

    related_tasks = [task for task in tasks if task.id in project.tasks]
    for task in related_tasks:
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
with open("tiny_tasks_shortlist.md", "w", encoding="utf-8") as f:
    f.write(markdown_tiny_tasks)