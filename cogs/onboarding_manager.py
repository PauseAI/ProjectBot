from typing import Dict
import discord
from airtable import Airtable

M_ABORT = "Cancelling process for {fields['Newcomer Name']}"
M_UNDO_ABORT = "Restarting process for {fields['Newcomer Name']}"

CONFIG = [
    {
        "name": "abort",
        "trigger": {
            "type": "react",
            "emoji": "⛔"
        },
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Aborted"
            },
            {
                "type": "message",
                "message": M_ABORT
            }
        ]
    },
    {
        "name": "undo_abort",
        "trigger": {
            "type": "unreact",
            "emoji": "⛔"
        },
        "conditions": [
            {
                "type": "database check ticked",
                "field_name": "Aborted",
                "message": M_UNDO_ABORT
            }
        ],
        "actions": [
            {
                "type": "database update untick",
                "field_name": "Aborted"
            },
            {
                "type": "message",
                "message": M_ABORT
            }
        ]
    }
]

def format_message(message: str, record: Dict) -> str:
    return message.format(
        record_id= record["id"],
        fields= record["fields"]
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

    def trigger_signature_from_reaction(self, payload: discord.RawReactionActionEvent) -> str:
        emoji = str(payload.emoji)
        if emoji in self.reserved_emojis:
            return f"react({emoji})"
        else:
            return f"react()"
        
    def trigger_signature_from_unreact(self, payload: discord.RawReactionClearEvent) -> str:
        emoji = str(payload.emoji)
        if emoji in self.reserved_emojis:
            return f"unreact({emoji})"
        else:
            return f"unreact()"

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
        return f"{stage_trigger['type']}({','.join(params)})"

    def build_triggers_lookup(self, config: Dict) -> Dict[str, Dict]:
        triggers_lookup = {}
        for stage in config:
            trigger_signature = self.trigger_signature_from_stage(stage["trigger"])
            triggers_lookup[trigger_signature] = stage
        return triggers_lookup
    
    async def reaction_trigger(self, record: Dict, table: Airtable, payload: discord.RawReactionActionEvent):
        """This is called when somebody reacts to a message in the onboarding channel"""
        signature = self.trigger_signature_from_reaction(payload)
        await self.handle_stage(signature, record, table, payload)
    
    async def clear_reaction_trigger(self, record: Dict, table: Airtable, payload: discord.RawReactionClearEvent):
        """This is called when somebody reacts to a message in the onboarding channel"""
        signature = self.trigger_signature_from_unreact(payload)
        await self.handle_stage(signature, record, table, payload)

    async def handle_stage(self, signature: str, record: Dict, table: Airtable, payload: discord.RawReactionActionEvent):
        stage = self.triggers_lookup.get(signature)
        if stage is None:
            print(f"Error: this reaction is not expected: {signature}")
            return
        # Now we know which stage we are dealing with
        # First we check the conditions
        for condition in stage.get("conditions", []):
            print(f"Condition: {condition['type']}")
            satisfied = False
            if condition["type"] == "database check ticked":
                satisfied = record.get(condition["field_name"], False)
            elif condition["type"] == "database check unticked":
                satisfied = not record.get(condition["field_name"], False)
            else:
                print(f"Error: unknown condition type: {condition['type']}")
                return
            if not satisfied and "message" in condition:
                format_message(condition["message"], record)
            if not satisfied:
                # We stop everything
                return
        for action in stage.get("actions", []):
            print(f"Action: {action['type']}")
            if action["type"] == "database update tick":
                table.update(record["id"], {action["field_name"]: True})
            elif action["type"] == "database update untick":
                table.update(record["id"], {action["field_name"]: False})
            elif action["type"] == "message":
                format_message(action["message"], record)
            else:
                print(f"Error: unknown action type: {action['type']}")
                return
            
ONBOARDING_MANAGER = OnboardingManager(CONFIG)