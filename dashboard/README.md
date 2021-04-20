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
DB_URI="postgres://xxavjkznrfvkik:1303d7d092dadc3f5d1e677ad2070528dc8ae19653b9af4545881e5ccd6cd6fa@ec2-54-154-101-45.eu-west-1.compute.amazonaws.com:5432/d98dsjrrujqqiu
" streamlit run app.py
```

# limitations

I'm recreating the db connection engine every time the page is reloaded, which makes no sense, i need to figure out a way to do this better.
