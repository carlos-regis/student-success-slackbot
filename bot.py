import os
from typing import Set

import pandas as pd
from sqlalchemy import create_engine
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# I used the following 2 lines of code because I was getting an SSL error. If 
# you don't get that error, feel free to comment them.
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def get_instructors_ids(client: WebClient) -> Set[str]:
    '''
    Gets the slack_ids of the instructors to save them from spam.
    '''
    response = client.conversations_members(channel="C01RBSVJ1D5")
    instructors_ids = response["members"]

    return set(instructors_ids)

def get_all_slack_ids(client: WebClient) -> Set[str]:
    '''
    Gets the slack_ids of all the human users in the workspace 
    (the ones that have lenght 11 - this is specific to this workspace).
    '''
    response = client.users_list()
    users = response["members"]
    user_ids = list(map(lambda u: u["id"], users))
    user_ids = [_id for _id in user_ids if len(_id) == 11]
    
    return set(user_ids)


def get_submitted_slack_ids() -> Set[str]:
    '''
    Gets the slack_ids of all the human users in the workspace 
    that have submitted the lu.
    (the ones that have lenght 11 - this is specific to this workspace).
    '''
    engine = create_engine(os.environ['DB_URI'])
    df = pd.read_sql(
        "select * from submission_db where length(slack_id) = 11",
        engine
    )
    submitted_slack_ids = set(
        df.loc[
            (df.learning_unit == int(os.environ["SLU"])) 
            & 
            (df.slack_id.str.len() == 11), 
            'slack_id'
        ]
    )

    return submitted_slack_ids


client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

all_slack_ids = get_all_slack_ids(client)
instructors_ids = get_instructors_ids(client)
submitted_slack_ids = get_submitted_slack_ids()
not_submitted_slack_ids = all_slack_ids - submitted_slack_ids - instructors_ids

print(
    len(all_slack_ids),
    len(instructors_ids),
    len(submitted_slack_ids),
    len(not_submitted_slack_ids),
)

text = f'''
You have not submitted SLU{os.environ["SLU"]} yet! 
Please do, the deadline is today!
If you need help, go to the week-{os.environ["SLU"]} channel and ask!
'''

n_messages_sent = 0
for slack_id in not_submitted_slack_ids:
    try:
        result = client.chat_postMessage(
            channel=slack_id,
            text=text
        )
        if result['ok']:
            n_messages_sent += 1
    except SlackApiError as e:
        print(f"Error: {e}")

print(n_messages_sent)
