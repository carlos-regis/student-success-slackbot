import requests
import json
import logging
import pandas as pd

MAX_ALLOWED_PAGES = 2
URL = 'https://prep-course-portal.ldsacademy.org/submissions/'
page = 0

submissions = []
while page < MAX_ALLOWED_PAGES:
    request = requests.get(URL)
    request.raise_for_status()

    response = json.loads(request.text)

    next_cursor = response.get('next')
    n_submissions = response.get('count')
    
    submissions += response.get("results")

    logging.info(f'Retrieved {len(submissions)}/{n_submissions} submissions')
    print(f'Retrieved {len(submissions)}/{n_submissions} submissions')
    URL = next_cursor
    page += 1

    if not next_cursor:
        break

submissions_df = pd.DataFrame(submissions)
print(submissions_df)

