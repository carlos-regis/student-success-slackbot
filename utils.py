import os
import logging
import re

import constants

user_slack_id_pattern = re.compile(r'^[UW][A-Z0-9]{10}$')


def check_valid_slack_id(slack_id: str) -> bool:
    return True if user_slack_id_pattern.match(slack_id) else False


def filter_valid_slack_ids(slack_ids: list) -> list:
    return [_id for _id in slack_ids if check_valid_slack_id(_id)]


def fix_slack_id(slack_id: str) -> str:
    return slack_id.replace('<', '').replace('>', '')


def create_logger(logger_name: str, logging_file: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(
        os.path.join(constants.LOGS_FOLDER, logging_file))
    file_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    console_formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":

    print(fix_slack_id("<U0509EC4H8V>"))
