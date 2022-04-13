import os
from typing import Set
import time
from cv2 import log
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from get_submissions import get_submitted_slack_ids
import logging

logging.basicConfig(level=logging.INFO)

INSTRUCTORS_CHANNEL_ID = "C036U6ZFEKC"
URL = "https://prep-course-portal.ldsacademy.org/submissions/"
SLU_ID = os.environ["SLU_ID"]

# Number of maximum attemps to post a message in a channel
MAX_ATTEMPTS = 5

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def get_instructors_ids(client: WebClient) -> Set[str]:
    """
    Gets the slack_ids of the instructors to save them from spam.
    """
    response = client.conversations_members(channel=INSTRUCTORS_CHANNEL_ID)
    instructors_ids = response["members"]

    return set(instructors_ids)


def get_all_slack_ids(client: WebClient) -> Set[str]:
    """
    Gets the slack_ids of all the human users in the workspace
    (the ones that have lenght 11 - this is specific to this workspace).
    """
    response = client.users_list()
    users = response["members"]
    user_ids = list(map(lambda u: u["id"], users))
    user_ids = [_id for _id in user_ids if len(_id) == 11]

    return set(user_ids)


def reminder_message(slu_id):
    slu_id_str = SLU_ID
    if len(slu_id_str) == 1:
        slu_id_str = "0" + slu_id_str

    text = f"""
    You have not submitted SLU{slu_id_str} yet! 
    Please do, the deadline is today!
    If you need help, go to the week-{slu_id_str} channel and ask!
    """
    return text


def send_message(slack_id, slu_id):
    """
    Send a Slack message to student to remind them to
    submit the SLU
    """
    while n < MAX_ATTEMPTS:
        n = 0
        try:
            result = client.chat_postMessage(
                channel="C03BB9M2UNR", text=reminder_message(slu_id)  # slack_id
            )
            if result["ok"]:
                n_messages_sent += 1
                logging.info(slack_id)
            time.sleep(1)
            break

        except SlackApiError as e:
            time.sleep(1)
            logging.warning(f"Error: {e}")
            n += 1

    if n == MAX_ATTEMPTS:
        logging.warning(
            "Number of max unsuccessful attempts reached. Message was not sent."
        )


if __name__ == "__main__":
    all_slack_ids = get_all_slack_ids(client)
    instructors_ids = get_instructors_ids(client)
    submitted_slack_ids = get_submitted_slack_ids(SLU_ID, URL)
    not_submitted_slack_ids = all_slack_ids - submitted_slack_ids - instructors_ids

    logging.info(f"Total number of Slack IDs: {len(all_slack_ids)}")
    logging.info(f"Number of Instructor IDs: {len(instructors_ids)}")
    logging.info(f"Number of IDs with submissions: {len(submitted_slack_ids)}")
    logging.info(f"Number of not submitted IDs: {len(not_submitted_slack_ids)}")

    logging.info(not_submitted_slack_ids)
    n_messages_sent = 0
    for slack_id in not_submitted_slack_ids:
        send_message(slack_id=slack_id, slu_id=SLU_ID)

    logging.info(
        f"{n_messages_sent} students have received a reminder message on SLU {SLU_ID}."
    )
