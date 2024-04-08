# Feature Plan: Tracking Email Onboarding

## Feature Description
When sending an email to a new member from the website, your #1 goal is to get them to join discord. With the bot, I will add fields in the Join table mentioning that someone is doing the onboarding there. The logic will be the same as for discord onboarding. And the process ends when the user’s discord id has been collected.

## Suggested Implementation
So there will be a new command that takes the discord id as the parameter. !onboarding discord <user_id>. I think it can accept numeric id or username.