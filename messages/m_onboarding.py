M_THREAD = "Thanks for indicating that {name} has posted an introduction"
M_REJOIN = "Thanks for indicating that {name} has rejoined discord"

M_ABORT = "Locking the onboarding process for {name}. To undo, remove your emoji."
M_UNDO_ABORT = "Unlocking the onboarding process for {name}"

M_ERROR_UNDO_ABORT = "Can't unlock, the onboarding process was not locked for {name}"
M_ERROR_ABORTED = "You can't do this, {name}'s onboarding process has been aborted"
M_ERROR_WRONG_RESEARCHER = "Error: {researcher_name} is already researching {name}" #todo add researcher name
M_ERROR_WRONG_ONBOARDER = "Error: {onboarder_name} is already onboarding {name}"
M_ERROR_NOT_RESEARCHED = "Error: {name} has not been researched yet."
M_ERROR_NOT_REPLIED = "{name} has not replied to you yet"
M_ERROR_NOT_MET = "You have not met {name} yet"
M_ERROR_WEBSITE = "Error: this stage is for a website onboarding only, not a discord onboarding"
M_ERROR_DISCORD = "Error: this stage is for a discord onboarding only, not a website onboarding"

M_START_RESEARCH_WEBSITE = "Thanks for starting the research on {name}. Their id is {db_id}"
M_START_RESEARCH_DISCORD = "Thanks for starting the research on {name}. Their id is {db_id}"
M_UNDO_START_RESEARCH = "You are no longer researching {name}. If that was a mistake, you can add your reaction again."

M_LOG_RESEARCH = "Thanks for logging your research on {name}. Logged: {text}"

M_END_RESEARCH_VIP = "Congratulations for identifying a VIP!"
M_END_RESEARCH_NOT_VIP = "Congratulations for finishing the research!"
M_UNDO_END_RESEARCH = "Action undone, research no longer complete"

M_START_ONBOARDING_DISCORD = """🌞Thank you so much for onboarding {name}🌞!{vip_sentence}
## Onboarding Guide
At this stage your goals are to get {name} to reply to you, and check if they are interested in becoming a contributing member to Pause AI.

If you are unsure how to start the conversation, feel free to use the following template.
```
Hi {name}! Welcome to Pause AI!
What brings you here? Are you interested in becoming a contributing member of the community? If so let's have a chat 🙂 I am part of the onboarding team so my role is to get you up and running and contributing to a project in no time - depending on your skills, interest, and the time you have to contribute
```

Once they have replied to you, please notify me by sending me the following command:
```
!onboarding {first_stage} {db_id}
```
"""
M_START_ONBOARDING_WEBSITE = """🌞Thank you so much for onboarding {name}🌞!
## Onboarding Guide - Website
At this stage your goal is to get {name} to join our discord community - this is where the magic happens!
Please contact them via email. If you need inspiration, you can find templates [here](https://docs.google.com/document/d/1Psbr38f7BxhRREndRYo_tn_d6Ta0UE_PoXX8wXqnhjQ/edit)
## About Them
**Name:** {name}
**Country:** {country}
**City:** {city}
**How do you want to help?**
{how_to_help}
**What types of action are you interested in?**
{types_of_action}
**Hours per week:** {hours_per_week}
**Email Address:** ```{email}```

Once they have signed up on discord, please send me their username like so:
```!onboarding discord <username> {db_id}```
"""

M_UNDO_START_ONBOARDING = """You are no longer onboarding {name}. If that was a mistake, you can add your reaction again."""

M_ONBOARDING_REPLIED = """🌞Amazing! {name} replied to you!🌞
## Onboarding Guide
At this stage your goals are to get {name} to:
- Sign up on the website
- Write an introduction
- Get them to join the next onboarding meeting
- Organise a face to face meeting with them

Once the face to face meeting is organised, please let me know by sending me the following command:
```
!onboarding met {db_id}
```
"""

M_ONBOARDING_MET = """🌞Awesome! A new contributing member,thanks to you!🌞
## Onboarding Guide
During this 1 on 1 meeting, your goal is to:
- Orient them around the discord
- Tell them about how we work, the different teams, the projects (high level)
- Talk about their skills, interests and the time they will be able to contribute
- Present them with projects that can suit them
- The next step for them is to pick a project or team. Once this is done you will introduce them to the project or team lead.

If you need a shortlist of our most important projects, you can send me:
```
!projects
```
If you need a shortlist of our tiny tasks that everyone should be able to contribute to, type:
```
!tasks
```
The last stage is the final check-in.
```
!onboarding checkin {db_id}
```
"""

M_ONBOARDING_CHECK_IN = """CONGRATS!
You have succesfully onboarded {name}"""

M_ONBOARDING_EMAIL = """Well done sending an email to {name}.
When they join discord, use this command to tell us their username:
```!onboarding discord {db_id} <username>```
"""

ON_DISCORD = """🌞Stellar!🌞
{name} can now go through the regular Discord onboarding pipeline!"""

USER_NOT_FOUND = """Unable to find this username on the Discord server: {user_name}.
The username can be found by opening someone's profile, just under their display name."""


# CAREFUL: the syntax of the following message matters for the retrieval
        # It should start with this exact sequence "emoji:" and end with the id under
        # double brackets
NEW_SIGNUP = """🆕: **{name}** from {country} signed up on the website! ||{record_id}||
> {how_to_help}"""

REMINDER = """- **{name}**. Command for next stage:```!onboarding {stage} {user_id}```"""