import logging
import os
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from get_submissions import get_submitted_slack_ids

URL = "https://prep-course-portal.ldsacademy.org/submissions/"
# WebClient instantiates a client that can call API methods
client = WebClient(
    token="xoxb-3654777008880-5117811696870-NC8S039rXHS2uHml3cfU4oDN")

logger = logging.getLogger(__name__)


def get_channel_users(channel_id: str):
    """
    Gets the slack_ids of the instructors to save them from spam.
    """
    response = client.conversations_members(channel=channel_id)
    users_ids = response["members"]

    return set(users_ids)


def send_message(slack_id: str, message: str):
    try:
        # Call the chat.postMessage method using the WebClient
        result = client.chat_postMessage(
            channel=slack_id,
            text=message
        )
        logger.info(result)
        print(result)

    except SlackApiError as e:
        logger.error(f"Error posting message: {e}")


def get_users():
    try:
        result = client.users_list()
        users = result["members"]
        user_ids = list(map(lambda u: u["id"], users))
        user_ids = [_id for _id in user_ids if len(_id) == 11]
        return user_ids

    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")


if __name__ == "__main__":
    bot_channel = "C03K2AWRKRU"
    hackermen_channel = "C03JMC52LUC"
    member_id = "U03JG3FHM6H"

    # print(get_users())
    # send_message(channel_id, "Hey friends")
    send_message(member_id, ' '.join(get_submitted_slack_ids(3, URL)))
    # print(get_channel_users(bot_channel))
