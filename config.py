import yaml
import os

projects_db_id = "0aa5ed2c00034cdd8e3923c5af11e237"
tasks_db_id = "d67272ac6a8c4511bde0fa7db7da86c9"
projects_db_id_staging = "16d604fad7364ee5b1d111e33b739310"
tasks_db_id_staging = "86dc1d61ac814cae8a850be348092758"
openai_organization = "org-DP5OE4ilCc68WugMCjHvlNCN"
airtable_base_id = 'appWPTGqZmUcs3NWu'
airtable_base_id_staging = 'appFY0WxDonY1Jgb1'
onboarding_channel_id = 1174807044990193775
onboarding_channel_id_staging = 1214198954321907845
polling_interval = 300
admin_user_ids = [
    252771041464680449, # Maxime F
    211238287522791425, # Joep
    228252768056508437, # Nathan
    732773275238793266, # Felix
    312360228555456533, # Will P
    232972493957103618, # Pato
    346706777305251840, # Chris G
]

# ----- SECRETS -------------------
try:
    with open('secrets.yml', 'r') as file:
        secrets = yaml.safe_load(file)
except FileNotFoundError:
    secrets = {}

discord_bot_secret = ( os.environ["DISCORD_BOT_SECRET"] 
                      if "DISCORD_BOT_SECRET" in os.environ 
                      else secrets["discord_bot_secret"] )
discord_bot_secret_staging = ( os.environ["DISCORD_BOT_SECRET_STAGING"] 
                      if "DISCORD_BOT_SECRET_STAGING" in os.environ 
                      else secrets["discord_bot_secret_staging"] )
notion_integration_token = ( os.environ["NOTION_INTEGRATION_TOKEN"] 
                      if "NOTION_INTEGRATION_TOKEN" in os.environ 
                      else secrets["notion_integration_token"] )
openai_api_key = ( os.environ["OPENAI_API_KEY"] 
                      if "OPENAI_API_KEY" in os.environ 
                      else secrets["openai_api_key"] )
airtable_token = ( os.environ["AIRTABLE_TOKEN"] 
                      if "AIRTABLE_TOKEN" in os.environ 
                      else secrets["airtable_token"] )
