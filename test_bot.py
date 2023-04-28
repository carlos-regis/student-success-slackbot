import os
from typing import Set
from dotenv import load_dotenv

from slack_sdk import WebClient

import utils
import constants
import helpers

from submissions import get_slu_slack_ids

logger = utils.create_logger(
    'bot_logger', constants.LOG_FILE_BOT)

load_dotenv()
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])


def reminder_message(slu_id: int) -> str:
    return (
        f'Hi human friend!\n\n'
        f'You have *not* submitted the exercise for *SLU{str(slu_id).zfill(2)}* yet.\n\n'
        f'*No worries, there is no deadline.* This is just a reminder to keep you on track.\n\n'
        f'*If you need help, please go to the respective week channel and ask.*\n\n'
        f'If you have indeed submitted the exercise for this SLU, your slack id was invalid. No need to submit it again.\n'
    )


def get_slu_submission_slack_ids(slu_id: int):
    all_slack_ids = helpers.get_workspace_users(client)
    instructors_ids = helpers.get_channel_users(client,
                                                constants.INSTRUCTORS_CHANNEL_ID)
    students_ids = all_slack_ids - instructors_ids

    # Filtering for submissions with a valid student slack id
    submitted_slack_ids = set([
        slack_id for slack_id in get_slu_slack_ids(slu_id, constants.URL_SUBMISSIONS_PORTAL) if slack_id in students_ids])

    not_submitted_slack_ids = sorted(students_ids - submitted_slack_ids)

    logger.info(f"Number of students: {len(students_ids)}")
    logger.info(
        f"Number of submissions for SLU{str(slu_id).zfill(2)}: {len(submitted_slack_ids)}")
    logger.info(
        f"Number of missing submissions for SLU{str(slu_id).zfill(2)}: {len(not_submitted_slack_ids)}")

    return students_ids, submitted_slack_ids, not_submitted_slack_ids


def get_slu_submission_summary(slu_id: int) -> str:

    students_ids, submitted_slack_ids, not_submitted_slack_ids = get_slu_submission_slack_ids(
        slu_id)

    return (
        f'*Basic summary for SLU{str(slu_id).zfill(2)} submissions:*\n\n'
        f' - Number of students: *{len(students_ids)}*\n'
        f' - Number of submissions: *{len(submitted_slack_ids)}*\n'
        f' - Number of missing submissions: *{len(not_submitted_slack_ids)}*'
    )


if __name__ == "__main__":
    CR_ID = "U04PVQS7EG7"
    MH_ID = "U04QZTRC524"

    # print(helpers.get_workspace_users(client))
    # print(helpers.get_channel_users(client, constants.INSTRUCTORS_CHANNEL_ID))
    # helpers.send_message(client, CR_ID, reminder_message(slu_id=0))
    # helpers.send_message(client, CR_ID, get_slu_submission_summary(slu_id=0))
