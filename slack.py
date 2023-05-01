import time
from typing import Set

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import utils
import constants

logger = utils.create_logger(
    'slack_logger', constants.LOG_FILE_SLACK)


def slack_error_handler(exception: Exception, error_message: str):
    assert exception.response["ok"] is False
    assert exception.response["error"]
    logger.error(f"{error_message}: {exception.response['error']}")


def get_workspace_users(client: WebClient) -> Set[str]:
    """
    Gets the slack_id's for all the human users of the workspace.
    """
    try:
        response = client.users_list()
        slack_ids = set(
            list(map(lambda user: user["id"], response["members"])))
        slack_ids.remove(constants.SLACK_BOT_ID)

        return slack_ids

    except SlackApiError as exception:
        slack_error_handler(exception, "Error getting workspace users")

        return set()


def get_channel_users(client: WebClient, channel_id: str) -> Set[str]:
    """
    Gets the slack_ids of the instructors to save them from spam.
    """
    try:
        response = client.conversations_members(channel=channel_id)
        slack_ids = set(utils.filter_valid_slack_ids(response["members"]))

        return slack_ids

    except SlackApiError as exception:
        slack_error_handler(exception, "Error getting channel users")


def send_message(client: WebClient, slack_id: str, message: str):
    """
        Send a Slack message to student to remind them to
        submit the SLU
    """
    for retries in range(constants.MAX_MESSAGE_ATTEMPTS):
        try:
            response = client.chat_postMessage(
                channel=slack_id,
                text=message
            )
            if response["ok"]:
                logger.info(f"Message successfully sent to {slack_id}")
                time.sleep(constants.REQUEST_RETRY_WAITING_TIME)
            break

        except SlackApiError as exception:
            time.sleep(constants.MESSAGE_RETRY_WAITING_TIME)
            slack_error_handler(
                exception, f"Error on Slack API on retry #{retries} for {slack_id}")

    if retries == constants.MAX_MESSAGE_ATTEMPTS - 1:
        logger.error(
            "Message not sent. The maximum retries was reached"
        )

    return None


def send_image(client: WebClient, slack_id: str, initial_comment: str, file_name: str) -> bool:
    try:
        # Call the files.upload method using the WebClient
        # Uploading files requires the `files:write` scope
        response = client.files_upload(
            channels=slack_id,
            initial_comment=initial_comment,
            file=file_name
        )
        logger.info(response)

        return True

    except SlackApiError as exception:
        slack_error_handler(
            exception, f"Error uploading file")

        return False
