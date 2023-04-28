import time
from typing import Set
import json
import logging
import pandas as pd

import requests
from requests.exceptions import HTTPError

import utils
import constants

logger = utils.create_logger(
    'submissions_logger', constants.LOG_FILE_SUBMISSIONS)


def get_submissions(url: str) -> pd.DataFrame:
    """
    Gets all submissions from the Submissions Portal
    """
    submissions = []
    for page in range(constants.MAX_ALLOWED_PAGES):
        for connection_retry in range(constants.MAX_CONNECTION_RETRIES):
            try:
                request = requests.get(url)
                request.raise_for_status()
            except HTTPError as exception:
                if exception.response.status_code in constants.HTTP_STATUS_RETRY_CODES:
                    logger.exception(
                        f"Connection to the Submissions Portal API failed"
                    )
                    time.sleep(constants.HTTP_RETRY_WAITING_TIME)
                    continue
                else:
                    logger.exception(
                        f"Connection to the Submissions Portal API failed"
                    )
                    raise

            try:
                response = json.loads(request.text)
                submissions += response.get("results")
                url = response.get("next")
                time.sleep(constants.REQUEST_RETRY_WAITING_TIME)
                if page % constants.PAGE_TRACKING_INTERVAL == 0:
                    logger.debug(
                        f"Fetched {len(submissions)} out of {response.get('count')} submissions"
                    )
                break

            except Exception as exception:
                logger.exception(
                    f"Connection to the Submissions Portal API failed"
                )
                time.sleep(constants.HTTP_RETRY_WAITING_TIME)

        if connection_retry == constants.MAX_CONNECTION_RETRIES - 1:
            logger.error(
                "Connection not successful. The maximum retries was reached"
            )
            break

        if not url:
            logger.info(f"Fetched {len(submissions)} submissions")
            break

    return pd.DataFrame(submissions).sort_values(by=['slackid', 'learning_unit'])


def filter_valid_submissions(submissions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter by dataframe by valid slack_ids
    """

    return submissions_df[submissions_df.slackid.apply(
        utils.check_valid_slack_id)].reset_index()


def get_slu_slack_ids(slu_id: int, url: str, filter_valid_slack_id: bool = True) -> Set[str]:
    """
    Gets a set of slack_ids of the submissions for a specific SLU
    """
    submissions_df = get_submissions(url)
    if filter_valid_slack_id:
        submissions_df = filter_valid_submissions(submissions_df)

    return set(utils.filter_valid_slack_ids(
        submissions_df.slackid[submissions_df.learning_unit == slu_id]))


if __name__ == "__main__":

    df = get_submissions(constants.URL_SUBMISSIONS_PORTAL)

    ids = get_slu_slack_ids(0, constants.URL_SUBMISSIONS_PORTAL)
    print(ids)
