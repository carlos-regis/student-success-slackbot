# hosted on

https://student-success-dashboard.herokuapp.com

# deploy

```bash
# first time
heroku login
heroku create student-success-dashboard --buildpack heroku/python
heroku git:remote student-success-dashboard
heroku config:set DB_URI="postgresql://wouldntyouliketoknow"

# every time

# this is because the app is in the dashboard/ folder
# otherwise it would be git push heroku <branch>:main
git subtree push --prefix dashboard heroku main

```

# run local

```bash
DB_URI="postgresql://wouldntyouliketoknow" streamlit run app.py
```
