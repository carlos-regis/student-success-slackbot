import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# I used the following 2 lines of code because I was getting an SSL error. If 
# you don't get that error, feel free to comment them.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# SLACK_BOT_TOKEN is the token of the bot. To get it, you should go to:
#  https://api.slack.com/apps, select your app, under Features select 
# OAuth & Permissions and copy Bot User OAuth Token into your .env
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))


# insert code to get a bunch of member IDs from heroku

for channel_id in heroku_channel_ids:
    try:
        # Call the conversations.list method using the WebClient
        result = client.chat_postMessage(
            channel=channel_id,
            text="ola ricardo" # Insert your text here
        )
        print(result)

    except SlackApiError as e:
        print(f"Error: {e}")