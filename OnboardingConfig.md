# Discord Bot Configuration System

This is a configuration system for Pause AI's Discord bot that supports the volunteers onboarding pipeline.

## Configuration Structure

The configuration is defined in a Python list called `CONFIG`. Each item in the list represents a specific configuration for a particular action or event.

### Configuration Item

Each configuration item is a dictionary with the following keys:

- `name`: The name of the configuration item.
- `trigger`: The trigger that activates the configuration item.
- `conditions` (optional): A list of conditions that must be met for the configuration item to be executed.
- `actions`: A list of actions to be performed when the configuration item is triggered and all conditions are met.

### Trigger

The `trigger` dictionary defines the event or action that triggers the configuration item. It has the following keys:

- `type`: The type of the trigger. Possible values include:
  - `"react"`: Triggered when a specific emoji reaction is added to a message.
  - `"unreact"`: Triggered when a specific emoji reaction is removed from a message.
  - `"command"`: Triggered when a specific command is executed.
- `emoji` (optional): The emoji that triggers the configuration item (required for `"react"` and `"unreact"` triggers).
- `command` (optional): The command that triggers the configuration item (required for `"command"` triggers).
- `subcommand` (optional): The subcommand of the command that triggers the configuration item (required for `"command"` triggers).

### Conditions

The `conditions` list contains a set of conditions that must be met for the configuration item to be executed. Each condition is a dictionary with the following keys:

- `type`: The type of the condition. Possible values include:
  - `"database check unticked"`: Checks if a specific field in the database is unticked.
  - `"database check ticked"`: Checks if a specific field in the database is ticked.
  - `"check param value"`: Checks if a specific parameter has a certain value.
  - `"database check is onboarder"`: Checks if the user is an onboarder.
  - `"database check is researcher"`: Checks if the user is a researcher.
  - `"database check no researcher"`: Checks if there is no researcher assigned.
  - `"database check no onboarder"`: Checks if there is no onboarder assigned.
- `field_name` (optional): The name of the field in the database to check (used with `"database check unticked"` and `"database check ticked"` conditions).
- `param_name` (optional): The name of the parameter to check (used with `"check param value"` condition).
- `param_value` (optional): The expected value of the parameter (used with `"check param value"` condition).
- `message` (optional): The error message to display if the condition is not met.

### Actions

The `actions` list contains a set of actions to be performed when the configuration item is triggered and all conditions are met. Each action is a dictionary with the following keys:

- `type`: The type of the action. Possible values include:
  - `"database update tick"`: Updates a specific field in the database by ticking it.
  - `"message"`: Sends a message.
  - `"database set researcher"`: Sets the current user as the researcher.
  - `"database reset researcher"`: Resets the researcher.
  - `"database log research"`: Logs the research result in the database.
  - `"database update untick"`: Updates a specific field in the database by unticking it.
  - `"database set onboarder"`: Sets the current user as the onboarder.
  - `"database reset onboarder"`: Resets the onboarder.
- `field_name` (optional): The name of the field in the database to update (used with `"database update tick"`, `"database update untick"`, and `"database log research"` actions).
- `condition` (optional): A condition to be checked for the action to take place (see Conditions chapter above)
- `message` (optional): The message to send (used with `"message"` action).

## Standard Conditions

The configuration system also defines some standard conditions that can be reused across multiple configuration items. These conditions are defined as dictionaries at the beginning of the configuration file.

- `NOT_ABORTED`: Checks if the "Aborted" field in the database is unticked.
- `DATABASE_WEBSITE`: Checks if the `table_id` parameter has a value of "j". Corresponds to the table "Join Pause AI"
- `DATABASE_DISCORD`: Checks if the `table_id` parameter has a value of "o". Corresponds to the table "Onboarding Events"
- `CHECK_IS_ONBOARDER`: Checks if the current user is an onboarder.
- `CHECK_IS_RESEARCHER`: Checks if the current user is a researcher.

These standard conditions can be included in the `conditions` list of a configuration item to apply the corresponding checks.

## Messages

The configuration system uses predefined messages stored in the `messages.m_onboarding` module. These messages are referenced by their variable names (e.g., `M_ERROR_ABORTED`, `M_ABORT`, etc.) in the `message` field of the actions.
