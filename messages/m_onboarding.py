M_THREAD = "Thanks for indicating that {name} has posted an introduction"
M_REJOIN = "Thanks for indicating that {name} has rejoined discord"

M_ABORT = "Locked the onboarding process for {name}. To undo, remove your emoji."
M_UNDO_ABORT = "Unlocked the onboarding process for {name}"

M_ERROR_UNDO_ABORT = "Error: Can't unlock, the onboarding process was not locked for {name}."
M_ERROR_ABORTED = "Error: You can't do this, {name}'s onboarding process has been aborted and locked."
M_ERROR_WRONG_RESEARCHER = "Error: {researcher_name} is already researching {name}" #todo add researcher name
M_ERROR_WRONG_ONBOARDER = "Error: {onboarder_name} is already onboarding {name}"
M_ERROR_NOT_RESEARCHED = "Error: {name} has not been researched yet."
M_ERROR_NOT_CONTRIBUTOR = "Error: {name} has not been marked as a contributor yet"
M_ERROR_NOT_MET = "Error: You have not met {name} yet"
M_ERROR_WEBSITE = "Error: this stage is for a website onboarding only, not a discord onboarding"
M_ERROR_DISCORD = "Error: this stage is for a discord onboarding only, not a website onboarding"

M_START_RESEARCH_WEBSITE = """🌞Thanks for starting the research on {name}!🌞
Please refer to the [onboarding manual](https://docs.google.com/document/d/1aG4Z4x-qIs2uAcy5DS8bNtYikleLOp4ACvoDFlzCPyI) if you do not know what to look for.
## About Them
**Name:** {name}
**Country:** {country}
**City:** {city}
**Linkedin:** {linkedin}
**How do you want to help?**
{how_to_help}
**What types of action are you interested in?**
{types_of_action}
**Joined Discord:** {joined_discord}
**Discord Username:** {discord_username}
**Hours per week:** {hours_per_week}
**Email Address:** ```{email}```
Once you have researched them, please log your findings with the following command:
```
!research log {db_id} <your findings>
```
"""
M_START_RESEARCH_DISCORD = """🌞Thanks for starting the research on {name}!🌞
Please refer to the [onboarding manual](https://docs.google.com/document/d/1aG4Z4x-qIs2uAcy5DS8bNtYikleLOp4ACvoDFlzCPyI) if you do not know what to look for.

Once you have researched them, please log your findings with the following command:
```
!research log {db_id} <your findings>
```
"""
M_UNDO_START_RESEARCH = "You are no longer researching {name}. If that was a mistake, you can react with the 🔍 emoji again."

M_LOG_RESEARCH = """Thanks for logging your research on {name}! 

Logged:
```
{text}
```

Now indicate whether they are a VIP(🥇) or not(🥈) by reacting with the corresponding emoji.
"""

M_END_RESEARCH_VIP = "Congratulations for identifying a VIP!"
M_END_RESEARCH_NOT_VIP = "Congratulations for finishing the research!"
M_UNDO_END_RESEARCH = "Action undone, research no longer complete"

M_START_ONBOARDING_DISCORD = """🌞Thank you so much for onboarding {name}🌞!{vip_sentence}
## Onboarding Guide
At this stage the main goal is to **check if they are willing to contribute more than 2 hours a week**.
You also want to get them to:
- sign-up on the website
- write an introduction if they have not
- join the next onboarding meeting
- point them to a "new joiner guide" (does not exist yet)

Research Output:
```
{research_result}
```

We recommend that you use this message
```
Hi {name}! Welcome to Pause AI!
What brings you here? Are you interested in becoming a contributing member of the community? If so let's have a chat 🙂 I am part of the onboarding team so my role is to get you up and running and contributing to a project in no time - depending on your skills, interest, and the time you have to contribute
```

If they are willing to contribute, move them to the next stage using the following command. 
```
!onboarding contributor {db_id}
```
"""
M_START_ONBOARDING_WEBSITE = """🌞Thank you so much for onboarding {name}🌞!{vip_sentence}
## Onboarding Guide - Website
At this stage your goal is to get {name} to join our discord community - this is where the magic happens!
Please contact them via email. If you need inspiration, you can find templates [here](https://docs.google.com/document/d/1Psbr38f7BxhRREndRYo_tn_d6Ta0UE_PoXX8wXqnhjQ/edit)
## About Them
**Name:** {name}
**Country:** {country}
**City:** {city}
**Linkedin:** {linkedin}
**How do you want to help?**
{how_to_help}
**What types of action are you interested in?**
{types_of_action}
**Joined Discord:** {joined_discord}
**Discord Username:** {discord_username}
**Hours per week:** {hours_per_week}
**Email Address:** ```{email}```
Research Output:
```
{research_result}
```
Once you have emailed them, use the following command to move on to the next stage:
```!onboarding emailed {db_id}```
"""

M_UNDO_START_ONBOARDING = """You are no longer onboarding {name}. If that was a mistake, you can react with your emoji again."""

M_ONBOARDING_EMAILED = """
Thanks for emailing {name}! 

Now you just need to be on the lookout for new joiners, or a reply from them. 
Once they have signed up on discord, please send me their Discord username like so:
```!onboarding discord {db_id} <discord username> ```
"""

M_ONBOARDING_CONTRIBUTOR = """🌞Amazing! {name} is willing to contribute more than 2 hours a week!🌞
## Onboarding Guide
At this stage you should organise a face to face meeting with them.
Also make sure that they have:
- Signed up on the website
- Writen an introduction
- Attended an onboarding meeting (or planning to attend)

If you need help, check out this detailed [guide](https://docs.google.com/document/d/1NHf1fvx5k6bzSr7dsn-1fyqINUZPAacvk0LL6CYY6iE/edit) for the 1 on 1 meeting
The main goal is to get them motivated, oriented, and willing to join a team or project. 

If you need a shortlist of our most important projects, you can use this command:
```
!projects
```
If you need a shortlist of our tiny tasks that everyone should be able to contribute to, use this command:
```
!tasks
```

Once the face to face meeting has happened, use the following command:
```
!onboarding met {db_id}
```
"""

M_ONBOARDING_MET = """🌞Awesome! And almost there! 🌞
## Onboarding Guide
After this meeting, the newcomer should spend some time thinking about which team or project they want to contribute to.
It is important to organise a check-in meeting with them the next week. This will be the final step of this onboarding.

During the check-in meeting, the goal is to:
- make sure that everything is going smoothly for them, answer any remaining questions that they have
- get them to sign the [volunteer form](https://airtable.com/appWPTGqZmUcs3NWu/pag7ztLh27Omj5s2n/form)
- get the output of their reflection, and have them officially joining a team or project

Once this meeting is over, use the following command to access the final, and most important stage.
```
!onboarding checkin {db_id}
```
"""

M_ONBOARDING_CHECK_IN = """🌞This is the final stage for {name}! 🌞
Now that you have had the final check-in and your newcomer has picked their team or project, your final job is to select a mentor for them and introduce them.
It should normally be the team or project lead, but otherwise you will have to find someone else in the organisation.

Once the mentor has been picked and introduced, use this final command to tell us their Discord Username
```
!onboarding mentor {db_id} <mentor username>
```
"""

M_ONBOARDING_MENTOR = """🥳🥳CONGRATULATIONS!🥳🥳
You have succesfully onboarded {name}."""

M_ONBOARDING_EMAILED = """Well done sending an email to {name}!
When they join discord, use this command to tell us their username:
```!onboarding joined_discord {db_id} <username>```
"""

M_ONBOARDING_JOINED_DISCORD = """🥳🥳CONGRATULATIONS!🥳🥳
Now, {name} can go through the Discord onboarding pipeline!
"""

USER_NOT_FOUND = """Unable to find this username on the Discord server: {user_name}.
The username can be found by opening someone's profile, just under their display name."""


# CAREFUL: the syntax of the following message matters for the retrieval
        # It should start with this exact sequence "emoji:" and end with the id under
        # double brackets
NEW_SIGNUP = """🆕: **{name}** from {country} signed up on the website! ||{record_id}||
> {how_to_help}"""

REMINDER = """- **{name}**. Command for next stage:```!onboarding {stage} {user_id}```"""