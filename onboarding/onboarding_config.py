from messages.m_onboarding import *
from airtable_client import TABLES

# -------------
# STANDARD CONDITIONS
# --------------
NOT_ABORTED = {
    "type": "database check unticked",
    "field_name": "Aborted",
    "message": M_ERROR_ABORTED
}
DATABASE_WEBSITE = {
    "type": "check param value",
    "param_name": "table_id",
    "param_value": TABLES.join_pause_ai.table_name,
    "message": M_ERROR_WEBSITE
}
DATABASE_DISCORD = {
    "type": "check param value",
    "param_name": "table_id",
    "param_value": TABLES.onboarding_events.table_name,
    "message": M_ERROR_DISCORD
}
CHECK_IS_ONBOARDER = {
    "type": "database check is onboarder",
    "message": M_ERROR_WRONG_ONBOARDER
}
CHECK_IS_RESEARCHER = {
    "type": "database check is researcher",
    "message": M_ERROR_WRONG_RESEARCHER
}

VERSION = "0.3"
CONFIG = [
    {
        "name": "thread",
        "trigger": {
            "type": "react",
            "emoji": "🧵"
        },
        "actions": [
            {
                "type": "message",
                "message": M_THREAD,
            }
        ]
    },
    {
        "name": "rejoin",
        "trigger": {
            "type": "react",
            "emoji": "🔁"
        },
        "actions": [
            {
                "type": "message",
                "message": M_REJOIN,
            }
        ]
    },
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
        "name": "red_flag",
        "trigger": {
            "type": "react",
            "emoji": "🚩"
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
                "message": M_ERROR_UNDO_ABORT
            }
        ],
        "actions": [
            {
                "type": "database update untick",
                "field_name": "Aborted"
            },
            {
                "type": "message",
                "message": M_UNDO_ABORT
            }
        ]
    },
    {
        "name": "undo_red_flag",
        "trigger": {
            "type": "unreact",
            "emoji": "🚩"
        },
        "conditions": [
            {
                "type": "database check ticked",
                "field_name": "Aborted",
                "message": M_ERROR_UNDO_ABORT
            }
        ],
        "actions": [
            {
                "type": "database update untick",
                "field_name": "Aborted"
            },
            {
                "type": "message",
                "message": M_UNDO_ABORT
            }
        ]
    },
    {
        "name": "undo_rejoin",
        "trigger": {
            "type": "unreact",
            "emoji": "🔁"
        },
        "conditions": [
            {
                "type": "database check ticked",
                "field_name": "Aborted",
                "message": M_ERROR_UNDO_ABORT
            }
        ],
        "actions": [
            {
                "type": "database update untick",
                "field_name": "Aborted"
            },
            {
                "type": "message",
                "message": M_UNDO_ABORT
            }
        ]
    },
    {
        "name": "start_research",
        "trigger": {
            "type": "react",
            "emoji": "🔍"
        },
        "conditions": [
            NOT_ABORTED,
            {
                "type": "database check no researcher",
                "message": M_ERROR_WRONG_RESEARCHER
            }
        ],
        "actions": [
            {
                "type": "database set researcher",
            },
            {
                "type": "message",
                "condition": DATABASE_WEBSITE,
                "message": M_START_RESEARCH_WEBSITE
            },
            {
                "type": "message",
                "condition": DATABASE_DISCORD,
                "message": M_START_RESEARCH_DISCORD
            }
        ]
    },
    {
        "name": "undo_start_research",
        "trigger": {
            "type": "unreact",
            "emoji": "🔍"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_RESEARCHER
        ],
        "actions": [
            {
                "type": "database reset researcher",
            },
            {
                "type": "message",
                "message": M_UNDO_START_RESEARCH
            }
        ]
    },
    {
        "name": "log_research",
        "trigger": {
            "type": "command",
            "command": "research",
            "subcommand": "log"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_RESEARCHER
        ],
        "actions": [
            {
                "type": "database log research",
                "field_name": "Research Result"
            },
            {
                "type": "message",
                "message": M_LOG_RESEARCH
            }
        ]
    },
    {
        "name": "end_research_vip",
        "trigger": {
            "type": "react",
            "emoji": "🥇"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_RESEARCHER
        ],
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Researched"
            },
            {
                "type": "database update tick",
                "field_name": "Is VIP"
            },
            {
                "type": "message",
                "message": M_END_RESEARCH_VIP
            }
        ]
    },
    {
        "name": "undo_end_research_vip",
        "trigger": {
            "type": "unreact",
            "emoji": "🥇"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_RESEARCHER
        ],
        "actions": [
            {
                "type": "database update untick",
                "field_name": "Researched"
            },
            {
                "type": "database update untick",
                "field_name": "Is VIP"
            },
            {
                "type": "message",
                "message": M_UNDO_END_RESEARCH
            }
        ]
    },
    {
        "name": "end_research_not_vip",
        "trigger": {
            "type": "react",
            "emoji": "🥈"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_RESEARCHER
        ],
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Researched"
            },
            {
                "type": "message",
                "message": M_END_RESEARCH_NOT_VIP
            }
        ]
    },
    {
        "name": "undo_end_research_not_vip",
        "trigger": {
            "type": "unreact",
            "emoji": "🥈"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_RESEARCHER
        ],
        "actions": [
            {
                "type": "database update untick",
                "field_name": "Researched"
            },
            {
                "type": "database update untick",
                "field_name": "Is VIP"
            },
            {
                "type": "message",
                "message": M_UNDO_END_RESEARCH
            }
        ]
    },
    {
        "name": "start_onboarding",
        "trigger": {
            "type": "react"
        },
        "conditions": [
            NOT_ABORTED,
            {
                "type": "database check no onboarder",
                "message": M_ERROR_WRONG_ONBOARDER
            },
            {
                "type": "database check ticked",
                "field_name": "Researched",
                "message": M_ERROR_NOT_RESEARCHED
            },
        ],
        "actions": [
            {
                "type": "database set onboarder"
            },
            {
                "type": "message",
                "condition": DATABASE_WEBSITE,
                "message": M_START_ONBOARDING_WEBSITE
            },
            {
                "type": "message",
                "condition": DATABASE_DISCORD,
                "message": M_START_ONBOARDING_DISCORD
            },
        ]
    },
    {
        "name": "undo_start_onboarding",
        "trigger": {
            "type": "unreact"
        },
        "conditions": [
            NOT_ABORTED,
            CHECK_IS_ONBOARDER
        ],
        "actions": [
            {
                "type": "database reset onboarder"
            },
            {
                "type": "message",
                "message": M_UNDO_START_ONBOARDING
            }
        ]
    },
    {
        "name": "onboarding_contributor",
        "trigger": {
            "type": "command",
            "command": "onboarding",
            "subcommand": "contributor"
        },
        "conditions": [
            NOT_ABORTED,
            DATABASE_DISCORD, # this is for the discord pipeline only
            CHECK_IS_ONBOARDER
        ],
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Contributor"
            },
            {
                "type": "message",
                "message": M_ONBOARDING_CONTRIBUTOR
            }
        ]
    },
    {
        "name": "onboarding_met",
        "trigger": {
            "type": "command",
            "command": "onboarding",
            "subcommand": "met"
        },
        "conditions": [
            NOT_ABORTED,
            DATABASE_DISCORD, # this is for the discord pipeline only
            CHECK_IS_ONBOARDER,
            {
                "type": "database check ticked",
                "field_name": "Contributor",
                "message": M_ERROR_NOT_CONTRIBUTOR,
            }
        ],
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Face Meeting"
            },
            {
                "type": "message",
                "message": M_ONBOARDING_MET
            }
        ]
    },
    {
        "name": "onboarding_checkin",
        "trigger": {
            "type": "command",
            "command": "onboarding",
            "subcommand": "checkin"
        },
        "conditions": [
            NOT_ABORTED,
            DATABASE_DISCORD, # this is for the discord pipeline only
            CHECK_IS_ONBOARDER,
            {
                "type": "database check ticked",
                "field_name": "Face Meeting",
                "message": M_ERROR_NOT_MET,
            }
        ],
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Check In"
            },
            {
                "type": "message",
                "message": M_ONBOARDING_CHECK_IN
            }
        ]
    },
    {
        "name": "onboarding_mentor",
        "trigger": {
            "type": "command",
            "command": "onboarding",
            "subcommand": "mentor"
        },
        "conditions": [
            NOT_ABORTED,
            DATABASE_DISCORD, # this is for the discord pipeline only
            CHECK_IS_ONBOARDER,
        ],
        "actions": [
            {
                "type": "database set mentor",
            },
            {
                "type": "message",
                "message": M_ONBOARDING_MENTOR
            }
        ]
    },
    {
        "name": "onboarding_emailed",
        "trigger": {
            "type": "command",
            "command": "onboarding",
            "subcommand": "emailed"
        },
        "conditions": [
            NOT_ABORTED,
            DATABASE_WEBSITE, # this is for the discord pipeline only
            CHECK_IS_ONBOARDER
        ],
        "actions": [
            {
                "type": "database update tick",
                "field_name": "Email Sent"
            },
            {
                "type": "message",
                "message": M_ONBOARDING_EMAILED
            }
        ]
    },
    {
        "name": "onboarding_joined_discord",
        "trigger": {
            "type": "command",
            "command": "onboarding",
            "subcommand": "joined_discord"
        },
        "conditions": [
            NOT_ABORTED,
            DATABASE_WEBSITE, # this is for the discord pipeline only
            CHECK_IS_ONBOARDER
        ],
        "actions": [
            {
                "type": "database update field",
                "field_name": "Discord Id",
                "param_name": "provided_user_id"
            },
            {
                "type": "database update field",
                "field_name": "Discord Username",
                "param_name": "provided_user_name"
            },
            {
                "type": "message",
                "message": M_ONBOARDING_JOINED_DISCORD
            }
        ]
    }
]