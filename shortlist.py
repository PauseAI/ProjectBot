from airtable_client import TABLES
from dataclasses import dataclass
from typing import List

@dataclass
class Project:
    id: str
    name: str
    discord_url: str
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

# The ID of the database you want to retrieve properties from
DESCRIPTION = True

def get_project(record) -> Project:
    fields = record["fields"]
    return Project(
        id = record["id"],
        name=fields['Name'],
        discord_url=fields.get('Discord Link', ""),
        description=fields.get('Short Description',""),
        skills=fields.get("Skills", []),
        priority={"": -1, "🔥": 0, "🔥🔥": 1, "🔥🔥🔥": 2}.get(fields.get("Priority",""), -1),
        needs_leadership=fields.get("Needs Leadership", False),
        tasks=fields.get("Tasks",[])
    )

def get_task(record) -> Task:
    fields = record["fields"]
    return Task(
        id = record["id"],
        name=fields['Name'],
        involvement=fields.get("Involvement", ""),
        needs_help = fields.get("Needs Help", False),
        skills=fields.get("Skills",[]),
        special_skills=fields.get("Specialised Skills", []),
        projects=fields.get("Projects", []),
        )

def format_project(project: Project):
    project_markdown = f"### {project.discord_url}"
    #project_markdown = f"### [{project.name}]({project.public_url})"

    skills = ", ".join('`' + skill + '`' for skill in project.skills)
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
    if len(task.projects) == 0:
        return ""
    project = [p for p in projects if p.id == task.projects[0]][0]
    skills = ", ".join('`' + skill + '`' for skill in task.skills)
    spec_skills = ", ".join('`' + skill + '`' for skill in task.special_skills)
    return f"- {project.discord_url} {task.name} **{skills} {spec_skills}**\n"

def get_markdown():
    markdown_tiny_tasks = """
## Biweekly Tiny Tasks Shortlist
In thread is a list of tiny tasks that most people should be able to contribute to immediately
"""
    markdown_output = """
## Biweekly Projects Shortlist
In thread is a shortlist of our most important projects, to help orient newcomers.
"""

    print("Grabbing Projects...")
    projects_results = TABLES.projects.get_all()
    projects = [get_project(record) for record in projects_results]

    print("Grabbing tasks...")
    tasks_results = TABLES.tasks.get_all()
    tasks = [get_task(record) for record in tasks_results]

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
    return markdown_output, markdown_tiny_tasks

if __name__ == "__main__":
    markdown_projects, markdown_tasks = get_markdown()
    with open("projects_shortlist.md", "w", encoding="utf-8") as f:
        f.write(markdown_projects)
    with open("tiny_tasks_shortlist.md", "w", encoding="utf-8") as f:
        f.write(markdown_tasks)