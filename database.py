from peewee import (
    SqliteDatabase, Model, BooleanField, FloatField,
    IntegerField, TextField, IntegrityError, DateTimeField
)
from playhouse.shortcuts import model_to_dict

import utils
import constants
logger = utils.create_logger(
    'database_logger', constants.LOG_FILE_DATABASE)

DB = SqliteDatabase('submissions.db')


class Submission(Model):
    submission_id = IntegerField(unique=True)
    created = DateTimeField()
    slackid = TextField()
    learning_unit = IntegerField()
    exercise_notebook = IntegerField()
    score = FloatField()

    class Meta:
        database = DB
        ordering = ('learning_unit', 'exercise_notebook', 'slackid', 'score')


def get_all_records():
    return [model_to_dict(obs) for obs in Submission.select()]


def delete_all_records() -> int:
    return Submission.delete().execute()


def save_records(submission: Submission) -> bool:
    try:
        submission.save()
        return True
    except IntegrityError as exception:
        DB.rollback()
        logger.error(exception)
        return False


def insert_many_records(dicts) -> bool:
    try:
        Submission.insert_many(dicts).execute()
        return True
    except IntegrityError as exception:
        DB.rollback()
        logger.error(exception)
        return False


def test_db():
    submission_dict = {'id': 2,
                       'created': '2023-02-27T20:09:38.479111Z',
                       'slackid': 'migueldias',
                       'learning_unit': 0,
                       'exercise_notebook': 1,
                       'score': 0.0}
    submission = Submission(
        submission_id=submission_dict['id'],
        created=submission_dict['created'],
        slackid=submission_dict['slackid'],
        learning_unit=submission_dict['learning_unit'],
        exercise_notebook=submission_dict['exercise_notebook'],
        score=submission_dict['score']
    )
    if save_records(submission):
        print("Records successfully saved!")


def get_last_submission_id() -> int:
    return Submission.select().order_by(Submission.submission_id.desc()).get().submission_id


def fix_slack_id_records(symbol_to_remove: str) -> int:
    submission_query = (Submission
                        .select()
                        .where(Submission.slackid.contains(symbol_to_remove)))
    for submission in submission_query:
        print(submission.slackid)
        submission.slackid = utils.fix_slack_id(submission.slackid)
        submission.save()

    return len(submission_query)


def check_slack_id() -> int:
    return Submission.select().order_by(Submission.slackid.desc()).get().slackid


def set_invalid_slack_ids(string_to_replace: str) -> int:
    submission_query = (Submission
                        .select()
                        .where(Submission.slackid.contains(string_to_replace)))
    for submission in submission_query:
        print(submission.slackid)
        submission.slackid = 'INVALID_SLACKID'
        submission.save()

    return len(submission_query)


def get_invalid_slack_ids() -> int:
    return (Submission
            .select()
            .where(Submission.slackid.contains('INVALID_SLACKID'))
            .count())


if __name__ == "__main__":
    DB.create_tables([Submission], safe=True)
    # test_db()
    # print(fix_slack_id_records('C04PVN0K1QF'))
    # print(check_slack_id())
    print(get_invalid_slack_ids())
