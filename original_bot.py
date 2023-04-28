import os
from typing import Set
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from submissions import get_submitted_slack_ids
import logging

logging.basicConfig(level=logging.INFO)

INSTRUCTORS_CHANNEL_ID = "C04QNS8B9PT"
URL = "https://prep-course-portal.ldsacademy.org/submissions/"
SLU_ID = int(os.environ["SLU_ID"])

# Number of maximum attemps to post a message in a channel
MAX_ATTEMPTS = 5

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])


def get_instructors_ids(client: WebClient, channel_id: str) -> Set[str]:
    """
    Gets the slack_ids of the instructors to save them from spam.
    """
    response = client.conversations_members(channel=channel_id)
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


def reminder_message(slu_id: int) -> str:
    slu_id_str = str(slu_id)
    if len(slu_id_str) == 1:
        slu_id_str = "0" + slu_id_str

    text = f"""
    Hi human friend!
    You have not submitted the SLU{slu_id_str} yet!
    If you need help, go to the respective SLU channel and ask!
    """
    return text


def send_message(slack_id: str, slu_id: int):
    """
    Send a Slack message to student to remind them to
    submit the SLU
    """
    n = 0
    while n < MAX_ATTEMPTS:
        try:
            result = client.chat_postMessage(
                channel=slack_id, text=reminder_message(slu_id)
            )
            if result["ok"]:
                logging.info(slack_id)
                time.sleep(0.1)
            break

        except SlackApiError as e:
            time.sleep(1)
            logging.warning(
                f"Error on Slack API on try #{n} for {slack_id}: {e}")
            n += 1

    if n == MAX_ATTEMPTS:
        logging.warning(
            "Number of max unsuccessful attempts reached. Message was not sent to {slack_id}."
        )


if __name__ == "__main__":
    all_slack_ids = get_all_slack_ids(client)
    instructors_ids = get_instructors_ids(client, INSTRUCTORS_CHANNEL_ID)
    submitted_slack_ids = get_submitted_slack_ids(SLU_ID, URL)
    not_submitted_slack_ids = all_slack_ids - submitted_slack_ids - instructors_ids

    logging.info(f"Total number of Slack IDs: {len(all_slack_ids)}")
    logging.info(f"Number of Instructor IDs: {len(instructors_ids)}")
    logging.info(f"Number of IDs with submissions: {len(submitted_slack_ids)}")
    logging.info(
        f"Number of not submitted IDs: {len(not_submitted_slack_ids)}")

    logging.info(not_submitted_slack_ids)
    n_messages_sent = 0
    for slack_id in not_submitted_slack_ids:
        send_message(slack_id=slack_id, slu_id=SLU_ID)
        n_messages_sent += 1

    logging.info(
        f"{n_messages_sent} students have received a reminder message on SLU {SLU_ID}."
    )
