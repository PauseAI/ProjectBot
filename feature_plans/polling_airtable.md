# Feature Plan: Polling Airtable

## Feature Description
Have a process running that polls airtable repeatedly and pushes specific events to the bot. The first example would be when somebody signs up on the website. This currently populates a table, but the airtable API offers no way to push events to a python script. Actually that is not true, there is a webhook API, but it looks very new and is not implemented in the python client yet. After a quick review, I believe that Polling is still a simpler implementation.
Back to the example, the python process would repeatedly query the database, and trigger events in the bot when a change happen.


## Suggested Implementation
- Only detects additions and deletions, not updates to entries in a table
- The key mechanism is keeping track of the list of record ids in a table. The first time it runs, it loads all the record ids from the database and stores them in memory. During every subsequent run, it downloads the record ids again and compares them to the ones in memory. If a change is detected, it calls any function that has requested to listen to additions or deletions in this table.
- Leveraging the asyncio library