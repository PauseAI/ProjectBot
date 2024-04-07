CANCEL = """You are no longer onboarding {name}. If that was a mistake, you can add your reaction again."""

INITIAL = """🌞Thank you so much for onboarding {name}🌞!
## Onboarding Guide
At this stage your goals are to get {name} to reply to you, and check if they are interested in becoming a contributing member to Pause AI.

If you are unsure how to start the conversation, feel free to use the following template.
```
Hi {name}! Welcome to Pause AI!
What brings you here? Are you interested in becoming a contributing member of the community? If so let's have a chat 🙂 I am part of the onboarding team so my role is to get you up and running and contributing to a project in no time - depending on your skills, interest, and the time you have to contribute
```

Once they have replied to you, please notify me by sending me the following command:
```
!onboarding replied {user_id}
```
"""

REPLIED = """🌞Amazing! {name} replied to you!🌞
## Onboarding Guide
At this stage your goals are to get {name} to:
- Sign up on the website
- Write an introduction
- Get them to join the next onboarding meeting
- Organise a face to face meeting with them

Once the face to face meeting is organised, please let me know by sending me the following command:
```
!onboarding met {user_id}
```
"""

MET = """🌞Awesome! A new contributing member,thanks to you!🌞
## Onboarding Guide
During this 1 on 1 meeting, your goal is to:
- Orient them around the discord
- Tell them about how we work, the different teams, the project (high level)
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
"""