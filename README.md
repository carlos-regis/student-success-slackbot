# student-success-slackbot

This repo contains a script to send messages to students who have not submitted a specific learning unit. When `bot.py` runs it will send the messages. This should be run locally and ad-hoc.

## Environment variables

* `SLACK_BOT_TOKEN` is the token of the bot. Find it under *Bot User OAuth Token* in [this link](https://api.slack.com/apps/A03BAU6RQ5S/install-on-team).
* `SLU_ID` the SLU number like 0 or 1.

## Run locally

```bash
python bot.py
```

## To do every year
* Add the bot app to the new Prep course workspace. [Here is the link to the app](https://api.slack.com/apps/A03BAU6RQ5S).
People with current access to the app:
    * Minh
    * Miguel
    * Juliana
    * Mariana 
* Update the `INSTRUCTORS_CHANNEL_ID` in the `bot.py`
* Add the bot to the instructors channel
