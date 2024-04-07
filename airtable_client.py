from airtable import Airtable
import config

TABLE_NAMES = [
    "Projects",
    "Tasks",
    "Onboarding Events"
]

class Tables:
    def __init__(self):
        self.staging = False
        self._tables = {}
        self._tables_staging = {}
        for table_name in TABLE_NAMES:
            self._tables[table_name] = Airtable(
                config.airtable_base_id, table_name, 
                api_key=config.airtable_token)
            self._tables_staging[table_name] = Airtable(
                config.airtable_base_id_staging, table_name, 
                api_key=config.airtable_token)
            
    def set_staging(self):
        self.staging = True

    def get_table(self, name: str) -> Airtable:
        assert name in TABLE_NAMES, f"There is no table named {name}"
        return self._tables_staging[name] if self.staging else self._tables[name]
    
    @property
    def projects(self) -> Airtable:
        return self.get_table("Projects")
    
    @property
    def tasks(self) -> Airtable:
        return self.get_table("Tasks")
    
    @property
    def onboarding_events(self) -> Airtable:
        return self.get_table("Onboarding Events")

TABLES = Tables()