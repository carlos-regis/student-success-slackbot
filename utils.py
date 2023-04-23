import re

user_id_pattern = re.compile(r'^[UW][A-Z0-9]{10}$')


def filter_valid_slack_ids(slack_ids: list) -> list:
    return [_id for _id in slack_ids if user_id_pattern.match(_id)]
