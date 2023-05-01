import summary
import constants

if __name__ == "__main__":

    # print(slack.get_workspace_users(client))
    # print(slack.get_channel_users(client, constants.INSTRUCTORS_CHANNEL_ID))
    summary.send_submissions_summary(constants.CR_ID)
