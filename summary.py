# Base packages
import submissions
import slack
import utils
import constants
import os
from dotenv import load_dotenv
from typing import Set, Union

# Main packages
import pandas as pd
from slack_sdk import WebClient
import matplotlib.pylab as plt
plt.style.use('ggplot')

# Custom packages

logger = utils.create_logger(
    'summary_logger', constants.LOG_FILE_SUMMARY)

load_dotenv()
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])


def get_students_ids() -> Set[str]:
    all_slack_ids = slack.get_workspace_users(client)
    instructors_ids = slack.get_channel_users(client,
                                              constants.INSTRUCTORS_CHANNEL_ID)
    return all_slack_ids - instructors_ids


def get_slu_submissions_slack_ids(slu_id: int):
    all_slack_ids = slack.get_workspace_users(client)
    instructors_ids = slack.get_channel_users(client,
                                              constants.INSTRUCTORS_CHANNEL_ID)
    students_ids = get_students_ids()

    # Filtering for submissions with a valid student slack id
    submitted_slack_ids = set([
        slack_id for slack_id in submissions.get_slu_slack_ids(slu_id)])

    not_submitted_slack_ids = sorted(students_ids - submitted_slack_ids)

    logger.info(
        f"SLU{str(slu_id).zfill(2)} - Number of students: {len(students_ids)}")
    logger.info(
        f"SLU{str(slu_id).zfill(2)} - Number of submissions: {len(submitted_slack_ids)}")
    logger.info(
        f"SLU{str(slu_id).zfill(2)} - Number of missing submissions: {len(not_submitted_slack_ids)}")

    return students_ids, submitted_slack_ids, not_submitted_slack_ids


def generate_slu_submissions_summary_plot(slu_id: int,
                                          n_submitted: int,
                                          n_missing: int):

    df_plot = pd.DataFrame(
        [{
            'submitted': n_submitted,
            'missing': n_missing
        }])

    ax = df_plot.plot.bar(figsize=(8, 4), legend=True, stacked=True,
                          title=f"Submissions for SLU{str(slu_id).zfill(2)}")
    plt.xticks([])

    plt.savefig(os.path.join(
        constants.IMG_FOLDER, constants.IMG_FILE_SLU))

    return None


def send_slu_submissions_summary(slack_id: str, slu_id: int) -> bool:
    students_ids, submitted_slack_ids, not_submitted_slack_ids = get_slu_submissions_slack_ids(
        slu_id)

    generate_slu_submissions_summary_plot(slu_id,
                                          len(submitted_slack_ids),
                                          len(not_submitted_slack_ids))
    slack.send_image(client,
                     slack_id,
                     f"*Submissions for SLU{str(slu_id).zfill(2)}*",
                     os.path.join(
                         constants.IMG_FOLDER, constants.IMG_FILE_SLU))

    summary_msg = (
        f'Students: *{len(students_ids)}* | '
        f'Submissions: *{len(submitted_slack_ids)}* | '
        f'Missing submissions: *{len(not_submitted_slack_ids)}*'
    )

    slack.send_message(
        client, slack_id, summary_msg)


def get_submissions_plot_data(df: pd.DataFrame) -> Union[pd.DataFrame, None]:
    '''
    Transform the submissions data into a dataframe ready to be plotted.

    :df: from get_submissions()
    :returns: a dataframe ready to be plotted
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


def generate_submissions_plot(df_plot: Union[pd.DataFrame, None]) -> Union[str, None]:
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
    plt.xlabel("Learning Unit")
    ax.margins(y=0.1)

    plt.savefig(os.path.join(
        constants.IMG_FOLDER, constants.IMG_FILE_GLOBAL))

    return None


def send_submissions_summary(slack_id: str):
    generate_submissions_plot(get_submissions_plot_data(
        submissions.get_submissions_from_db(filter_students=True)))

    slack.send_image(client,
                     slack_id,
                     f"*Submissions summary*",
                     os.path.join(
                         constants.IMG_FOLDER, constants.IMG_FILE_GLOBAL))


if __name__ == "__main__":
    # send_slu_submissions_summary(CR_ID, slu_id=0)
    send_submissions_summary(constants.CR_ID)
