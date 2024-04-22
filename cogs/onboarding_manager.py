from typing import Dict
import discord
from airtable import Airtable

from cogs.onboarding import reset_onboarder, reset_researcher, update_onboarder, update_researcher
from cogs.onboarding_config import CONFIG

class ConditionException(Exception):
    pass

def format_message(message: str, record: Dict, params: Dict) -> str:
    fields = record["fields"]
    return message.format(
        record_id = record["id"],
        name = fields.get("Newcomer Name", fields.get("Name", "Anonymous")),
        researcher_name = fields.get("Researcher Name", ""),
        onboarder_name = fields.get("Onboarder Name", ""),
        research_result = fields.get("Research Result", ""),
        is_vip = fields.get("Is VIP", False),
        country = fields.get("Country", ""),
        city = fields.get("City", ""),
        linkedin = fields.get("Linked", ""),
        how_to_help = fields.get("How do you want to help?", ""),
        types_of_action = fields.get("What types of action(s) would you be interested in?", ""),
        hours_per_week = fields.get("How many hours per week could you spend volunteering with PauseAI?", ""),
        email = fields.get("Email address", ""),
        joined_discord = fields.get("JoinedDiscord", "No"),
        discord_username = fields.get("Discord Username", ""),
        vip_sentence = "\nThey are a VIP 🥇" if fields.get("Is VIP") else "",
        first_stage = "replied" if params.get("table_id") == "o" else "email",
        **params
    )

class OnboardingManager:
    def __init__(self, config: Dict):
        self.config = config
        self.reserved_emojis: set[str] = self.get_reserved_emojis(config)
        self.triggers_lookup = self.build_triggers_lookup(config)

    def get_reserved_emojis(self, config: Dict) -> set[str]:
        """These emojis are used as specific triggers in the onboarding process"""
        reserved = set()
        for stage in config:
            if stage["trigger"]["type"] in ["react"]: #unreact as well or not?
                if "emoji" in stage["trigger"]:
                    reserved.add(stage["trigger"]["emoji"])
        return reserved

    def trigger_signature_from_reaction(self, emoji: str) -> str:
        if emoji in self.reserved_emojis:
            return f"react({emoji})"
        else:
            return f"react()"
        
    def trigger_signature_from_unreact(self, emoji: str) -> str:
        if emoji in self.reserved_emojis:
            return f"unreact({emoji})"
        else:
            return f"unreact()"
    
    def trigger_signature_from_command(self, command: str, subcommand: str) -> str:
        return f"command({command},{subcommand})"

    def trigger_signature_from_stage(self, stage_trigger: Dict) -> str:
        """For each stage, we derive the trigger signature"""
        if stage_trigger["type"] == "react":
            if "emoji" in stage_trigger:
                params = [stage_trigger["emoji"]]
                # react(<emoji>)
            else:
                params = []
                # react()
        if stage_trigger["type"] == "unreact":
            if "emoji" in stage_trigger:
                params = [stage_trigger["emoji"]]
                # unreact(<emoji>)
            else:
                params = []
                # unreact()
        if stage_trigger["type"] == "command":
            params = [stage_trigger["command"], stage_trigger["subcommand"]]
        return f"{stage_trigger['type']}({','.join(params)})"

    def build_triggers_lookup(self, config: Dict) -> Dict[str, Dict]:
        triggers_lookup = {}
        for stage in config:
            trigger_signature = self.trigger_signature_from_stage(stage["trigger"])
            triggers_lookup[trigger_signature] = stage
        return triggers_lookup
    
    async def reaction_trigger(self, user: discord.User, message: discord.Message, emoji: str, record: Dict, table: Airtable, params: Dict):
        """This is called when somebody reacts to a message in the onboarding channel"""
        signature = self.trigger_signature_from_reaction(emoji)
        await self.handle_stage(signature, user, message, emoji, record, table, params)
    
    async def clear_reaction_trigger(self, user: discord.User, message: discord.Message, emoji: str, record: Dict, table: Airtable, params: Dict):
        """This is called when somebody reacts to a message in the onboarding channel"""
        signature = self.trigger_signature_from_unreact(emoji)
        await self.handle_stage(signature, user, message, emoji, record, table, params)

    async def command_trigger(self, command: str, subcommand: str, user: discord.User, message: discord.Message, record: Dict, table: Airtable, params: Dict):
        signature = self.trigger_signature_from_command(command, subcommand)
        await self.handle_stage(signature, user, message, None, record, table, params)

    def solve_condition(self, condition: Dict, record: Dict, user: discord.User, params: Dict) -> bool:
        satisfied = False
        if condition["type"] == "database check ticked":
            satisfied = record["fields"].get(condition["field_name"], False)
        elif condition["type"] == "database check unticked":
            satisfied = not record["fields"].get(condition["field_name"], False)
        elif condition["type"] == "database check no researcher":
            satisfied = record["fields"].get("Researcher Id", "") == ""
        elif condition["type"] == "database check no onboarder":
            satisfied = record["fields"].get("Onboarder Id", "") == ""
        elif condition["type"] == "database check is researcher":
            satisfied = record["fields"].get("Researcher Id", "") == str(user.id)
        elif condition["type"] == "database check is onboarder":
            satisfied = record["fields"].get("Onboarder Id", "") == str(user.id)
        elif condition["type"] == "check param value":
            satisfied = params[condition["param_name"]] == condition["param_value"]
        else:
            raise ConditionException
            
        return satisfied

    async def handle_stage(self, signature: str, user: discord.User, message: discord.Message, emoji: str, record: Dict, table: Airtable, params: Dict):
        stage = self.triggers_lookup.get(signature)
        if stage is None:
            print(self.triggers_lookup.keys())
            print(f"Error: this trigger is not expected: {signature}")
            return
        print(f"Processing stage: {stage['name']}")
        # Now we know which stage we are dealing with
        # First we check the conditions
        for condition in stage.get("conditions", []):
            print(f"Condition: {condition['type']}")
            try:
                satisfied = self.solve_condition(condition, record, user, params)
            except ConditionException:
                print(f"Error: unknown condition type: {condition['type']}")
                return
            if not satisfied and "message" in condition:
                await user.send(format_message(condition["message"], record, params))
            if not satisfied:
                # We stop everything
                print("Condition not satisfied, ending stage.")
                return
        for action in stage.get("actions", []):
            print(f"Action: {action['type']}")
            if "condition" in action:
                condition = action["condition"]
                print(f"Evaluating condition attached to action: {condition['type']}")
                try:
                    satisfied = self.solve_condition(condition, record, user, params)
                except ConditionException:
                    print(f"Error: unknown condition type: {condition['type']}")
                    return
                if not satisfied:
                    print("Condition not satisfied, aborting action")
                    continue
            if action["type"] == "database update tick":
                table.update(record["id"], {action["field_name"]: True})
            elif action["type"] == "database update untick":
                table.update(record["id"], {action["field_name"]: False})
            elif action["type"] == "database set researcher":
                update_researcher(table, record["id"], user)
            elif action["type"] == "database set onboarder":
                update_onboarder(table, record["id"], user, emoji)
            elif action["type"] == "database reset researcher":
                reset_researcher(table, record["id"])
            elif action["type"] == "database reset onboarder":
                reset_onboarder(table, record["id"])
            elif action["type"] == "database log research":
                table.update(record["id"], {action["field_name"]: params["text"]})
            elif action["type"] == "database set mentor":
                table.update(record["id"], {
                    "Mentor Name": params["provided_user_display_name"],
                    "Mentor Id": params["provided_user_id"]
                })
            elif action["type"] == "database update field":
                table.update(record["id"], {action["field_name"]: params[action["param_name"]]}, typecast=True)
            elif action["type"] == "message":
                await user.send(format_message(action["message"], record, params))
            else:
                print(f"Error: unknown action type: {action['type']}")
                return
            
ONBOARDING_MANAGER = OnboardingManager(CONFIG)