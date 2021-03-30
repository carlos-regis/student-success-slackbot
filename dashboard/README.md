# hosted on

https://student-success-dashboard.herokuapp.com/submit

# deploy

```bash
# first time
heroku login
heroku create student-success-dashboard --buildpack heroku/python
heroku git:remote student-success-dashboard
heroku config:set DB_URI="wouldntyouliketoknow"

# every time

# this is because the app is in the dashboard/ folder
# otherwise it would be git push heroku <branch>:main
git subtree push --prefix dashboard heroku <branch>:main

```

# run local

```bash
DB_URI="wouldntyouliketoknow" streamlit run app.py
```
