import database
import constants
import utils
from requests.exceptions import HTTPError
import requests
import time
from typing import Set
import json

import pandas as pd

logger = utils.create_logger(
    'submissions_logger', constants.LOG_FILE_SUBMISSIONS)


def get_submissions_from_portal(base_url: str, last_submission_id: int) -> pd.DataFrame:
    """
    Gets all submissions from the Submissions Portal
    """
    submissions = []

    initial_page = (last_submission_id // constants.SUBMISSIONS_PER_PAGE) + 1
    page_url = f"{base_url}?page={initial_page}"

    for page in range(constants.MAX_ALLOWED_PAGES):
        for connection_retry in range(constants.MAX_CONNECTION_RETRIES):
            try:
                request = requests.get(page_url)
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
                page_url = response.get("next")
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

        if not page_url:
            logger.info(f"Fetched {len(submissions)} submissions")
            break

    submissions_df = pd.DataFrame(submissions)
    submissions_df.slackid = submissions_df.slackid.apply(utils.fix_slack_id)

    return submissions_df[submissions_df.id > last_submission_id]


def filter_valid_submissions(submissions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter by dataframe by valid slack_ids and score different than zero
    """
    filterd_submissions_df = submissions_df[submissions_df.score != 0.0]
    filterd_submissions_df[filterd_submissions_df.slackid.apply(
        utils.check_valid_slack_id)].reset_index(drop=True)

    # TODO: Needs to filter out duplicated submissions
    """
    4	1	<U0509EC4H8V>	19.0	April 28, 2023, 11:02 a.m.
    4	1	<U0509EC4H8V>	18.5	April 27, 2023, 1:04 p.m.
    4	1	<U0509EC4H8V>	18.5	April 27, 2023, 1 p.m.
    4	1	<U0509EC4H8V>	18.5	April 27, 2023, 12:51 p.m.
    """

    return filterd_submissions_df


def get_slu_slack_ids(slu_id: int, filter_valid_slack_id: bool = True) -> Set[str]:
    """
    Gets a set of slack_ids of the submissions for a specific SLU
    """
    submissions_df = get_submissions_from_db(filter_valid_slack_id)

    return set(utils.filter_valid_slack_ids(
        submissions_df.slackid[submissions_df.learning_unit == slu_id]))


def get_submissions_from_db(filter_valid_slack_id: bool = True) -> pd.DataFrame:
    '''Get all the submissions into a dataframe.'''

    update_submissions_db()

    submissions_dict = database.get_all_records()
    if not submissions_dict:
        return pd.DataFrame()

    submissions_df = pd.DataFrame(
        submissions_dict).drop('submission_id', axis=1)

    if filter_valid_slack_id:
        submissions_df = filter_valid_submissions(submissions_df)

    return submissions_df


def update_submissions_db():
    submissions_df = get_submissions_from_portal(constants.URL_SUBMISSIONS_PORTAL,
                                                 database.get_last_submission_id()).rename(
        columns={"id": "submission_id"})

    if database.insert_many_records(submissions_df.to_dict(orient='records')):
        success_msg = "Records successfully saved"
        logger.info(success_msg)
        return submissions_df
    else:
        error_msg = "Error saving the records"
        logger.info(error_msg)

    return pd.DataFrame()


if __name__ == "__main__":

    get_submissions_from_db()
