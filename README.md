# ProjectBot

This repository contains a python script running a Discord bot that fetches information from messages in forum channels and creates corresponding entries in a Notion database. It's designed to help with project management, allowing users to quickly transfer and track project details from Discord discussions to a structured Notion database.

## Prerequisites
Before you begin, ensure you have the following:

- Anaconda or Miniconda installed on your system. You can download Anaconda here or Miniconda here.
- A Discord bot token. Follow the instructions here to create a bot and obtain your token.
- A Notion integration token and a database ID. Follow the setup instructions here to create an integration and share a database with it.

# Setup
1. **Clone the Repository**

Clone this repository to your local machine using:

```sh
Copy code
git clone <repository-url>
cd <repository-directory>
```

2. **Create Conda Environment**

Create a new Conda environment using the environment.yml file included in the project:

```sh
Copy code
conda env create -f environment.yml
```

This will create a new environment named discord-notion-bot (or another name if specified in the environment.yml file) with all the necessary Python dependencies installed.

3. **Activate the Environment**

Activate the newly created Conda environment:

```sh
Copy code
conda activate discord-notion-bot
```

4. **Configure Secrets**

Create a secrets.yml file in the project directory with your Discord bot token and Notion integration details:

```yaml
Copy code
discord_bot_token: "YOUR_DISCORD_BOT_TOKEN"
notion_integration_token: "YOUR_NOTION_INTEGRATION_TOKEN"
notion_database_id: "YOUR_NOTION_DATABASE_ID"
```

Make sure to replace the placeholders with your actual tokens and IDs.

## Running the Bot
1. **Start the Bot**

With the Conda environment activated and the secrets configured, start the bot by running:

```sh
python bot.py
```


2. **Using the Bot**

In any Discord server where the bot is a member, navigate to a forum channel or a thread and type !track to trigger the bot. The bot will fetch information from the original post in the thread and create a corresponding entry in your Notion database.

## Notes
- Ensure the bot has the necessary permissions on your Discord server to read messages and access forum channels.
- The Notion database must be shared with your Notion integration for the bot to create entries.