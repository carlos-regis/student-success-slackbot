import db
import constants
import utils
from requests.exceptions import HTTPError
import requests
import os
import time
from typing import Set, Union
import json

import pandas as pd
import matplotlib.pylab as plt
plt.style.use('ggplot')


logger = utils.create_logger(
    'submissions_logger', constants.LOG_FILE_SUBMISSIONS)


def get_submissions_from_portal(url: str) -> pd.DataFrame:
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

    return pd.DataFrame(submissions)


def filter_valid_submissions(submissions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter by dataframe by valid slack_ids
    """

    return submissions_df[submissions_df.slackid.apply(
        utils.check_valid_slack_id)].reset_index()


def get_slu_slack_ids(slu_id: int, filter_valid_slack_id: bool = True) -> Set[str]:
    """
    Gets a set of slack_ids of the submissions for a specific SLU
    """
    submissions_df = get_submissions_from_db(filter_valid_slack_id)

    return set(utils.filter_valid_slack_ids(
        submissions_df.slackid[submissions_df.learning_unit == slu_id]))


def update_db():
    submissions_df = get_submissions_from_portal(constants.URL_SUBMISSIONS_PORTAL).rename(
        columns={"id": "submission_id"})

    if db.insert_many_records(submissions_df.to_dict(orient='records')):
        success_msg = "Records successfully saved"
        print(success_msg)
        logger.info(success_msg)
        return submissions_df
    else:
        error_msg = "Error saving the records"
        print(error_msg)
        logger.info(error_msg)

    return pd.DataFrame()


def get_submissions_from_db(filter_valid_slack_id: bool = True) -> pd.DataFrame:
    '''Get all the submissions into a dataframe.'''
    submissions_dict = db.get_all_records()
    if not submissions_dict:
        return pd.DataFrame()

    submissions_df = pd.DataFrame(
        submissions_dict).drop('submission_id', axis=1)

    if filter_valid_slack_id:
        submissions_df = filter_valid_submissions(submissions_df)

    return submissions_df


def get_submissions_plot_data(df: pd.DataFrame) -> Union[pd.DataFrame, None]:
    '''
    Transform the submissions data into a dataframe ready to be ploted.

    :df: from get_submissions()
    :returns: a dataframe ready to be ploted
    '''
    if df.empty:
        return None

    df_plot = (
        df
        .groupby(['learning_unit', 'exercise_notebook'])
        .slackid
        .count()
        .reset_index()
        .pivot(index='learning_unit', columns='exercise_notebook', values='slackid')
        .fillna(0)
        .astype(int)
    )

    return df_plot


def plot_submissions(df_plot: Union[pd.DataFrame, None]) -> Union[str, None]:
    '''
    Plot the submissions, get the plot ready to be displayed in template.
    https://stackoverflow.com/questions/61936775/how-to-pass-matplotlib-graph-in-django-template

    :df_plot: from get_submissions_plot_data()

    :returns: the encoded plot, ready to be passed to the template.
    '''
    if df_plot is None:
        return None

    ax = df_plot.plot.bar(figsize=(16, 4), legend=False, title=f"Submissions")
    ax.bar_label(ax.containers[0], label_type='edge', padding=5)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.xlabel("")
    ax.margins(y=0.1)

    plt.savefig(os.path.join(
        constants.IMG_FOLDER, constants.IMG_FILE_GLOBAL))

    return None


if __name__ == "__main__":

    # submissions_df = get_submissions_from_portal(constants.URL_SUBMISSIONS_PORTAL)

    # ids = get_slu_slack_ids(0, constants.URL_SUBMISSIONS_PORTAL)
    # print(ids)

    # update_db()
    # get_submissions_from_db()

    df_plot = get_submissions_plot_data(get_submissions_from_db())
    plot_submissions(df_plot)
