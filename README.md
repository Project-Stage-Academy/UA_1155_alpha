# Forum-Project-Stage-CC
Forum Project Stage CC Template Repo

## To run project locally:

 1) Make a copy of .env.example file, rename it to .env, and add your local settings. Ask any team members for email settings and secret key.
 2) Install Postgres and DBeaver, create Postgres DB
 3) Install Mongo DB and mongo compass
 4) If you use Windows: download redis from this link https://github.com/tporadowski/redis/releases. Install it and go to C:\Program Files\Redis and run redis-server.exe
 5) If you use linux or mac os, use pip install redis. Open new terminal and run "brew services start redis"
 6) Run "pip install -r requirements.txt" - to install all required libraries
 7) Run "python manage.py makemigrations" - to create migrations for DB
 8) Run "python manage.py migrate" - to apply those migrations 
 9) Run "python manage.py loaddata startups/industries.json" - to fill idustries table
 10) Run "python manage.py runserver" 
 11) Open second terminal and run "celery -A forum  worker -l info -P gevent" - to run celery

## To see all project endpoins:

Go to /yasg/swagger/
Here you can see all endpoints, json examples for requests and responses

## Team

> Or Contributors/People

<a href="https://github.com/NovitskaMariia">
    <img src="https://github.com/Project-Stage-Academy/UA_1155_alpha/assets/133953467/8886877b-d978-46f0-a905-ad79e62b19f6" alt="@NovitskaMariia" width="200" height="200">
</a>

[![@YuliaShap](https://avatars.githubusercontent.com/u/81677984?s=200&u=70db613ceba8b7cd7d3bd4c84636c99acc8e1119&v=4)](https://github.com/YuliaShap)
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


