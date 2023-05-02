import os
from typing import Set
from dotenv import load_dotenv

from slack_sdk import WebClient

import utils
import constants
import slack
import summary

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


def send_message_students(not_submitted_slack_ids, slu_id: int):

    n_messages_sent = 0
    for slack_id in not_submitted_slack_ids:
        slack.send_message(client,
                           slack_id=slack_id,
                           message=reminder_message(slu_id))
        n_messages_sent += 1

    logger.info(
        f"SLU{str(slu_id).zfill(2)} - {n_messages_sent} students have received a reminder message"
    )

    return None


if __name__ == "__main__":

    students_ids, submitted_slack_ids, not_submitted_slack_ids = summary.get_slu_submissions_slack_ids(
        constants.SLU_ID)

    send_message_students(not_submitted_slack_ids, constants.SLU_ID)

    # summary.send_slu_submission_summary(constants.INSTRUCTORS_CHANNEL_ID, slu_id=0)
    summary.send_submissions_summary(constants.INSTRUCTORS_CHANNEL_ID)
