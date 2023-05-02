from http import HTTPStatus

SLU_ID = 3

# Submissions
URL_SUBMISSIONS_PORTAL = "https://prep-course-portal.ldsacademy.org/submissions/"
MAX_ALLOWED_PAGES = 5000
MAX_CONNECTION_RETRIES = 20
RETRY_WAITING_TIME = 10
REQUEST_RETRY_WAITING_TIME = 0.2
PAGE_TRACKING_INTERVAL = 5
SUBMISSIONS_PER_PAGE = 10

# Slack
INSTRUCTORS_CHANNEL_ID = 'C04QNS8B9PT'
STUDENT_SUCCESS_BOT_ID = 'U05569Z4716'
CR_ID = "U04PVQS7EG7"
MH_ID = "U04QZTRC524"
SLACK_BOT_ID = 'USLACKBOT'

MESSAGE_RETRY_WAITING_TIME = 1
MAX_MESSAGE_ATTEMPTS = 5    # Number of maximum attemps to post a message in a channel

# Logs
LOGS_FOLDER = 'logs'
LOG_FILE_SUBMISSIONS = 'submissions.log'
LOG_FILE_BOT = 'bot.log'
LOG_FILE_SLACK = 'slack.log'
LOG_FILE_DATABASE = 'database.log'
LOG_FILE_SUMMARY = 'summary.log'

# Http Status
HTTP_STATUS_RETRY_CODES = [
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.INTERNAL_SERVER_ERROR,
    HTTPStatus.BAD_GATEWAY,
    HTTPStatus.SERVICE_UNAVAILABLE,
    HTTPStatus.GATEWAY_TIMEOUT,
]

# Visualization
IMG_FOLDER = 'media'
IMG_FILE_SLU = 'ldsa_prep_slu.png'
IMG_FILE_GLOBAL = 'ldsa_prep_global.png'
