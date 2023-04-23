import requests
import json
import logging
import pandas as pd
from typing import Set
import time

import utils

logging.basicConfig(level=logging.INFO)

MAX_ALLOWED_PAGES = 5000
URL_SUBMISSIONS = "https://prep-course-portal.ldsacademy.org/submissions/"
MAX_CONN_TRIES = 20


def get_submissions(url: str) -> pd.DataFrame:
    """
    Gets a list of all submissions from all SLUs from the Submissions
    Portal, by making a request to its API.
    """
    page = 0

    submissions = []
    while page < MAX_ALLOWED_PAGES:
        n = 0
        while n < MAX_CONN_TRIES:
            try:
                # Tries to connect to the Submissions Portal API
                request = requests.get(url)
                request.raise_for_status()
                response = json.loads(request.text)
                next_cursor = response.get("next")
                n_submissions = response.get("count")
                submissions += response.get("results")

                logging.info(
                    f"Retrieved {len(submissions)}/{n_submissions} submissions"
                )
                url = next_cursor
                page += 1
                time.sleep(0.1)
                break

            except Exception as e:
                # Portal is down
                logging.info(
                    f"Connection to Submission Portal API failed on {n} try with error: {e}"
                )
                # Waits 10 seconds until next try
                time.sleep(10)
                n += 1

        if n == MAX_CONN_TRIES:
            logging.warning(
                "Number of max unsuccessful attempts reached. Connection not successful."
            )
            break

        if not next_cursor:
            break

    return pd.DataFrame(submissions)


def get_submitted_slack_ids(slu_id: int, url: str) -> Set[str]:
    """
    Gets the slack_ids of all the human users in the workspace
    that have submitted the slu.
    """
    df = get_submissions(url)

    submitted_slack_ids = set(utils.filter_valid_slack_ids(
        df.slackid[df.learning_unit == slu_id]))

    return submitted_slack_ids


if __name__ == "__main__":
    ids = get_submitted_slack_ids(3, URL_SUBMISSIONS)
    print(ids)
