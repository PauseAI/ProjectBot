# Feature Plan: Jobs Class

## Feature Description
This is a technical features.
Add a “jobs” class in the bot. A job is simply a function that is executed at specific time intervals.
This will allow us to run scheduled jobs.

The first one should be a job for finding and populating discord ids of people from their indicated username, running a few times a day.

## Suggested Implementation
 It can be implemented very simply with asyncio. Following the example of the AirtablePolling class.