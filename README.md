# student-success-slackbot

This repo contains a script to send messages to students what have not submitted a specific learning unit. When `bot.py` runs it will send the messages. This should be run locally and ad-hoc.

## Environment variables

* `SLACK_BOT_TOKEN` is the token of the bot. To get it, you should go to: https://api.slack.com/apps, select your app, under Features select OAuth & Permissions. It's the "Bot User OAuth Token".
* `SLU_ID` the SLU number like 0 or 1.

## Run locally

```bash
python bot.py
```
