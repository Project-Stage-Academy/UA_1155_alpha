# Forum-Project-Stage-CC
Forum Project Stage CC Template Repo

**To run project locally:**

 1) Make a copy of .env.example file, rename it to .env, and add your local settings. Ask any team members for email settings and secret key.
 2) Create Postgres DB 
 3) Run "pip install -r requirements.txt" - to install all required libraries
 4) Run "python manage.py makemigrations" - to create migrations for DB
 5) Run "python manage.py migrate" - to apply those migrations 
 6) Run "python manage.py loaddata startups/industries.json" - to fill idustries table
 7) Run "python manage.py runserver" 
 8) Open second terminal and run "celery -A forum  worker -l info -P gevent" - to run celery

**To see all project endpoins:**

Go to /yasg/swagger/
Here you can see all endpoints, json examples for requests and responses

## Team

> Or Contributors/People

[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam) 
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)
[![@lhalam](https://avatars3.githubusercontent.com/u/3837059?s=100&v=4)](https://github.com/lhalam)  

- You can just grab their GitHub profile image URL
- You should probably resize their picture using `?s=200` at the end of the image URL.

---


