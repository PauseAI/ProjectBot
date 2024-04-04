from dataclasses import dataclass
from typing import List, Dict

def priority_from_tags(tags) -> int:
    if "Top Priority" in [t.name for t in tags]:
        return 2
    if "High Priority" in [t.name for t in tags]:
        return 1
    return 0

def skills_from_tags(tags) -> List[str]:
    return [tag.name for tag in tags 
        if tag.name not in ["High Priority", "Top Priority"]]

@dataclass
class Project:
    id: str = None
    name: str = None
    discord_url: str = None
    description: str = None 
    skills: list[str] = None
    priority: int = None
    needs_leadership: bool = None
    tasks: list[str] = None
    lead: str = None
    lead_id: str = None
    channel_id: int = None

    @staticmethod
    def from_airtable(record: Dict) -> "Project":
        fields = record["fields"]
        return Project(
            id = record["id"],
            name=fields['Name'],
            discord_url=fields.get('Discord Link', ""),
            description=fields.get('Short Description',""),
            skills=fields.get("Skills", []),
            priority={"": -1, "🔥": 0, "🔥🔥": 1, "🔥🔥🔥": 2}.get(fields.get("Priority",""), -1),
            needs_leadership=fields.get("Needs Leadership", False),
            tasks=fields.get("Tasks",[]),
            lead=fields.get("Lead", ""),
            lead_id=fields.get("Lead Id", ""),
        )
    
    def to_airtable(self) -> Dict:
        return {
            "Name": self.name,
            "Discord Link": self.discord_url,
            "Description": self.description,
            "Skills": self.skills,
            "Priority": ["🔥", "🔥🔥", "🔥🔥🔥", ""][self.priority],
            "Needs Leadership": self.needs_leadership,
            "Tasks": self.tasks,
            "Lead": self.lead,
            "Lead Id": self.lead_id,
        }
    
    @staticmethod
    def from_discord(msg) -> "Project":
        return Project(
            id = None,
            name = msg.channel.name,
            discord_url = f"https://discord.com/channels/{msg.guild.id}/{msg.channel.id}",
            description = msg.clean_content,
            skills = skills_from_tags(msg.channel.applied_tags),
            priority = priority_from_tags(msg.channel.applied_tags),
            lead = msg.author.display_name,
            lead_id = str(msg.author.id)
        )

@dataclass
class Task:
    id: str = None
    name: str = None
    involvement: str = None
    needs_help: bool = None
    skills: list[str] = None
    special_skills: list[str] = None
    projects: list[str] = None

    @staticmethod
    def from_airtable(record) -> "Task":
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
    
    def to_airtable(self) -> Dict:
        return {
            "Name": self.name,
            "Involvement": self.involvement,
            "Needs Help": self.needs_help,
            "Skills": self.skills,
            "Specialised Skills": self.special_skills,
            "Projects": self.projects,
        }