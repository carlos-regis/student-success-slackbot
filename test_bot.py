import os
from typing import Set
import logging
from dotenv import load_dotenv

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

import utils
from submissions import get_submitted_slack_ids

URL_SUBMISSIONS = "https://prep-course-portal.ldsacademy.org/submissions/"
INSTRUCTORS_CHANNEL_ID = "C04QNS8B9PT"
BOT_ID = "U05569Z4716"

load_dotenv()
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

logger = logging.getLogger(__name__)


def get_workspace_users() -> Set[str]:
    """
    Gets the slack_id's for all the human users of the workspace.
    """
    try:
        result = client.users_list()
        users = result["members"]
        slack_ids = list(map(lambda u: u["id"], users))
        slack_ids = set(utils.filter_valid_slack_ids(slack_ids))

        logger.info(slack_ids)
        return slack_ids

    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        error_message = f"Error getting workspace users: {e.response['error']}"

        logger.error(error_message)
        # print(error_message)


def get_channel_users(channel_id: str) -> Set[str]:
    """
    Gets the slack_ids of the instructors to save them from spam.
    """
    try:
        result = client.conversations_members(channel=channel_id)
        slack_ids = set(utils.filter_valid_slack_ids(result["members"]))

        logger.info(slack_ids)
        return slack_ids

    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        error_message = f"Error getting channel users: {e.response['error']}"

        logger.error(error_message)
        # print(error_message)


def reminder_message(slu_id: int) -> str:
    return (
        f'Hi human friend!\n'
        f'You have *not* submitted the *SLU{str(slu_id).zfill(2)}* yet!\n'
        f'*No worries, there are no deadlines.* Just a reminder to keep you on track.\n'
        f'If you need help, please go to the respective week channel and ask!\n'
        f'If you have indeed submitted the exercise for this SLU, please check if your slack id is correct!\n'
    )


def send_message(slack_id: str, message: str):
    try:
        result = client.chat_postMessage(
            channel=slack_id,
            text=message
        )
        logger.info(result)
        print(result)

    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]
        error_message = f"Error posting message: {e.response['error']}"
        logger.error(error_message)
        # print(error_message)


def get_slu_submission_summary(slu_id: int) -> str:
    all_slack_ids = get_workspace_users()
    instructors_ids = get_channel_users(INSTRUCTORS_CHANNEL_ID)
    students_ids = all_slack_ids - instructors_ids

    # Filtering for submissions with a valid student slack id
    submitted_slack_ids = set([
        slack_id for slack_id in get_submitted_slack_ids(slu_id, URL_SUBMISSIONS) if slack_id in students_ids])

    not_submitted_slack_ids = students_ids - submitted_slack_ids

    logging.info(f"Number of students: {len(students_ids)}")
    logging.info(f"Number of instructors: {len(instructors_ids)}")
    logging.info(
        f"Number of submissions for SLU{str(slu_id).zfill(2)}: {len(submitted_slack_ids)}")
    logging.info(
        f"Number of missing submissions for SLU{str(slu_id).zfill(2)}: {len(not_submitted_slack_ids)}")

    logging.info(not_submitted_slack_ids)

    return (
        f'*Basic summary for SLU{str(slu_id).zfill(2)} submissions:*\n\n'
        f' - Number of students: *{len(students_ids)}*\n'
        f' - Number of submissions: *{len(submitted_slack_ids)}*\n'
        f' - Number of missing submissions: *{len(not_submitted_slack_ids)}*'
    )


if __name__ == "__main__":
    CR_ID = "U04PVQS7EG7"
    MH_ID = "U04QZTRC524"

    # print(get_workspace_users())
    # print(get_channel_users(INSTRUCTORS_CHANNEL_ID))
    # send_message(CR_ID, reminder_message(slu_id=0))
    send_message(CR_ID, get_slu_submission_summary(slu_id=0))
    # send_message(CR_ID, ' '.join(get_submitted_slack_ids(3, URL_SUBMISSION)))
    # send_message(channel_id, "Hey friends")
