import os
from typing import Set
from dotenv import load_dotenv

from slack_sdk import WebClient

import utils
import constants
import helpers

from submissions import get_slu_slack_ids

load_dotenv()
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

logger = utils.create_logger(
    'bot_logger', constants.LOG_FILE_BOT)


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


def send_message_students(not_submitted_slack_ids, slu_id: int):

    n_messages_sent = 0
    for slack_id in not_submitted_slack_ids:
        helpers.send_message(client,
                             slack_id=slack_id,
                             message=reminder_message(slu_id))
        n_messages_sent += 1

    logger.info(
        f"{n_messages_sent} students have received a reminder message on SLU{str(slu_id).zfill(2)}"
    )

    return None


def get_slu_submission_summary(students_ids, submitted_slack_ids, not_submitted_slack_ids, slu_id: int) -> str:

    return (
        f'*Basic summary for SLU{str(slu_id).zfill(2)} submissions:*\n\n'
        f' - Number of students: *{len(students_ids)}*\n'
        f' - Number of submissions: *{len(submitted_slack_ids)}*\n'
        f' - Number of missing submissions: *{len(not_submitted_slack_ids)}*'
    )


if __name__ == "__main__":
    students_ids, submitted_slack_ids, not_submitted_slack_ids = get_slu_submission_slack_ids(
        constants.SLU_ID)

    send_message_students(not_submitted_slack_ids, constants.SLU_ID)

    # helpers.send_message(client, constants.INSTRUCTORS_CHANNEL_ID, get_slu_submission_summary(
    #     students_ids, submitted_slack_ids, not_submitted_slack_ids, constants.SLU_ID))
