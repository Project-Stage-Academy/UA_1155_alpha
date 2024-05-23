# Forum-Project-Stage-CC
Forum Project Stage CC Template Repo

## To run project locally:

 1) Make a copy of .env.example file, rename it to .env, and add your local settings. Ask any team members for email settings and secret key.
 2) Install Postgres and DBeaver, create Postgres DB 
 3) Install Mongo DB and mongo compass
 4) Run "pip install -r requirements.txt" - to install all required libraries
 5) Run "python manage.py makemigrations" - to create migrations for DB
 6) Run "python manage.py migrate" - to apply those migrations 
 7) Run "python manage.py loaddata startups/industries.json" - to fill idustries table
 8) Run "python manage.py runserver" 
 9) Open second terminal and run "celery -A forum  worker -l info -P gevent" - to run celery

## To see all project endpoins:

Go to /yasg/swagger/
Here you can see all endpoints, json examples for requests and responses

## Team

> Or Contributors/People

[![@AlexanderSychev2005](https://avatars.githubusercontent.com/u/49594203?v=4&s=200)](https://github.com/AlexanderSychev2005)
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


