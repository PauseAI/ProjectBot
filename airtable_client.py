from airtable import Airtable
import config

projects_table = Airtable(config.airtable_base_id, config.projects_table_name, api_key=config.airtable_token)
tasks_table = Airtable(config.airtable_base_id, config.tasks_table_name, api_key=config.airtable_token)
projects_table_staging = Airtable(config.airtable_base_id_staging, config.projects_table_name, api_key=config.airtable_token)
tasks_table_staging = Airtable(config.airtable_base_id_staging, config.tasks_table_name, api_key=config.airtable_token)
onboarding_events_table = Airtable(config.airtable_base_id, config.onboarding_events_table_name, api_key=config.airtable_token)
onboarding_events_table_staging = Airtable(config.airtable_base_id_staging, config.onboarding_events_table_name, api_key=config.airtable_token)

class Tables:
    def __init__(self):
        self.staging = False
    def set_staging(self):
        self.staging = True
    @property
    def projects(self):
        return projects_table_staging if self.staging else projects_table
    @property
    def tasks(self):
        return tasks_table_staging if self.staging else tasks_table
    @property
    def onboarding_events(self):
        return onboarding_events_table_staging if self.staging else onboarding_events_table

TABLES = Tables()