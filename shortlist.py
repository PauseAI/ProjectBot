from airtable_client import TABLES
from typing import List
from data_model import Project, Task

# The ID of the database you want to retrieve properties from
DESCRIPTION = True
LEGEND = """
**Legend**:
🟢: Tiny Task   -  Can be done in a few minutes
🟡: Small Task  -  One off, low involvement
🟠: Medium Task -  Regular involvement or big one off
🔴: Big Task    -  Multiple hour per week
"""

def format_project(project: Project, all_tasks: List[Task], show_description = False):
    project_markdown = f"### {project.discord_url}"
    #project_markdown = f"### [{project.name}]({project.public_url})"

    skills = ", ".join('`' + skill + '`' for skill in project.skills)
    project_markdown += f" {skills}"
    project_markdown += "\n"
    if show_description and project.description:  # Handle optional description
        project_markdown += project.description+"\n"

    if project.needs_leadership:
        project_markdown += "- 💡Needs Project Leadership💡\n"

    related_tasks = [task for task in all_tasks if task.id in project.tasks]
    for task in related_tasks:
        if not task.needs_help:
            continue
        project_markdown += format_task(task)

    project_markdown += "\n"
    return project_markdown

def format_task(task: Task):
    involvement_map = {
        "Tiny": "🟢", 
        "Small": "🟡",
        "Medium": "🟠",
        "Big": "🔴"
    }
    involvement_symbol = involvement_map.get(task.involvement, "")
    skills = ", ".join('`' + skill + '`' for skill in task.skills)
    spec_skills = ", ".join('`' + skill + '`' for skill in task.special_skills)
    return f"- {involvement_symbol} {task.name} **{skills} {spec_skills}**\n"

def format_task_oneline(task: Task, projects: List[Project]):
    if len(task.projects) == 0:
        project_url = ""
    else:
        project_url = [p for p in projects if p.id == task.projects[0]][0].discord_url
    skills = ", ".join('`' + skill + '`' for skill in task.skills)
    spec_skills = ", ".join('`' + skill + '`' for skill in task.special_skills)
    return f"- {project_url} {task.name} **{skills} {spec_skills}**\n"

def get_all_projects() -> List[Project]:
    projects_results = TABLES.projects.get_all()
    projects = [Project.from_airtable(record) for record in projects_results]
    return projects

def get_all_tasks() -> List[Task]:
    tasks_results = TABLES.tasks.get_all()
    tasks = [Task.from_airtable(record) for record in tasks_results]
    return tasks

def get_shortlist_tasks(all_projects: List[Project], all_tasks: List[Task]) -> str:
    markdown_tiny_tasks = ""
    for task in all_tasks:
        if not task.needs_help or not task.involvement == "Tiny":
            continue
        markdown_tiny_tasks += format_task_oneline(task, all_projects)
    
    return markdown_tiny_tasks

def get_shortlist_projects(all_projects: List[Project], all_tasks: List[Task], show_description = False) -> str:
    markdown_output = ""
    for project in projects:
        if project.priority != 2: 
            continue
        markdown_output += format_project(project, all_tasks, show_description)
    markdown_output += LEGEND
    
    return markdown_output

if __name__ == "__main__":
    print("Grabbing Projects...")
    projects = get_all_projects()

    print("Grabbing tasks...")
    tasks = get_all_tasks()

    markdown_projects = """## Biweekly Projects Shortlist
In thread is a shortlist of our most important projects, to help orient newcomers.

"""
    markdown_projects += get_shortlist_projects(projects, tasks, DESCRIPTION)
    
    markdown_tasks = """## Biweekly Tiny Tasks Shortlist
    In thread is a list of tiny tasks that most people should be able to contribute to immediately

"""
    markdown_tasks += get_shortlist_tasks(projects, tasks)

    with open("projects_shortlist.md", "w", encoding="utf-8") as f:
        f.write(markdown_projects)
    with open("tiny_tasks_shortlist.md", "w", encoding="utf-8") as f:
        f.write(markdown_tasks)