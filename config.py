import yaml
import os
from typing import List, Any

_SECRETS = ["DISCORD_BOT_SECRET", "OPENAI_API_KEY", "AIRTABLE_TOKEN"]

class Config:
    def __init__(self, config_file: str, secrets_file: str = None):
        self._staging = False
        self._staging_vars = {}
        self._prod_vars = {}

        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)

        try:
            # This file does not have to exist. In production, secrets are stored
            # in environment variables. This is for easy local development
            with open(secrets_file, 'r') as file:
                secrets = yaml.safe_load(file)
        except FileNotFoundError:
            secrets = {}

        for var_name, d in config_data.items():
            self._prod_vars[var_name] = d["prod"]
            self._staging_vars[var_name] = d["staging"]

        for var_name in _SECRETS:
            if var_name in secrets:
                self._prod_vars[var_name] = secrets[var_name]["prod"]
                self._staging_vars[var_name] = secrets[var_name]["staging"]
            else:
                self._prod_vars[var_name] = os.environ[var_name]
                #self._staging_vars[var_name] = os.environ[var_name]

    def set_staging(self):
        self._staging = True
    
    def set_prod(self):
        self._staging = False

    def get(self, var_name: str) -> Any:
        return self._staging_vars[var_name] if self._staging else self._prod_vars[var_name]
        
    @property
    def openai_organization(self) -> str:
        return self.get("openai_organization")
    
    @property
    def airtable_base_id(self) -> str:
        return self.get("airtable_base_id")
    
    @property
    def onboarding_channel_id(self) -> int:
        return self.get("onboarding_channel_id")
    
    @property
    def polling_interval(self) -> int:
        return self.get("polling_interval")
    
    @property
    def admin_user_ids(self) -> List[str]:
        return self.get("admin_user_ids")
    
    @property
    def discord_bot_secret(self) -> str:
        return self.get("DISCORD_BOT_SECRET")
    
    @property
    def openai_api_key(self) -> str:
        return self.get("OPENAI_API_KEY")
    
    @property
    def airtable_token(self) -> str:
        return self.get("AIRTABLE_TOKEN")

CONFIG = Config("config.yml", "secrets.yml")