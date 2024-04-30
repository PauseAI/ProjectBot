from airtable import Airtable
from config import CONFIG

TABLE_NAMES = [
    "Projects",
    "Tasks",
    "Onboarding Events",
    "Members",
    "Volunteers",
    "Teams"
]

class Tables:
    def __init__(self):
        self.staging = False
        self._tables = {}
        self._tables_staging = {}
        self.reset()
    
    def reset(self):
        for table_name in TABLE_NAMES:
            self._tables[table_name] = Airtable(
                CONFIG.airtable_base_id, table_name, 
                api_key=CONFIG.airtable_token)

    def get_table(self, name: str) -> Airtable:
        assert name in TABLE_NAMES, f"There is no table named {name}"
        return self._tables[name]
    
    @property
    def projects(self) -> Airtable:
        return self.get_table("Projects")
    
    @property
    def tasks(self) -> Airtable:
        return self.get_table("Tasks")
    
    @property
    def onboarding_events(self) -> Airtable:
        return self.get_table("Onboarding Events")
    
    @property
    def members(self) -> Airtable:
        return self.get_table("Members")
    
    @property
    def volunteers(self) -> Airtable:
        return self.get_table("Volunteers")
    
    @property
    def teams(self) -> Airtable:
        return self.get_table("Teams")

TABLES = Tables()