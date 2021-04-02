# student-success-slackbot

This repo contains a script to send messages to students what have not submitted a specific learning unit. When `bot.py` runs it will send the messages. This should be run locally and ad-hoc.

Under the folder `dashboard` there is a dashboard that displays how many students have completed each learning unit.

# environment variables for `bot.py`

* `DB_URI` the db uri like `postgresql://lslslslsls`
* `SLACK_BOT_TOKEN` is the token of the bot. To get it, you should go to: https://api.slack.com/apps, select your app, under Features select OAuth & Permissions. It's the "Bot User OAuth Token".
* `SLU` the slu number like `00` or `01`
