# deploy

```bash
# first time
heroku login
heroku create student-success-dashboard --buildpack heroku/python
heroku git:remote student-success-dashboard

# every time
git push heroku <branch>:main
git subtree push --prefix dashboard heroku <branch>:main
git subtree push --prefix dashboard heroku dashboard:main
```

# run local

```bash
DB_URI="wouldntyouliketoknow" streamlit run app.py
```
