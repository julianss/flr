# Flare
Framework for creating business web applications. Basically, it's a fully functioning generic app (backend with generic endpoint, user management, access control, etc. and frontend with CRUD functionality, record searching, report generation, etc) and you just define your domain-specific models and business logic and the layout of the views and menus.

It was inspired by [Odoo](https://odoo.com).

- Back-end built with: Python (Flask and Peewee)
- Front-end build with: Svelte

# Dependencies
- python at least 3.5.2
- node 14

# Database support
Although Peewee supports more than PostgreSQL and MySQL, automatic migrations are provided by peewee-db-evolve, which supports only those two. For now, though, PostgreSQL is hardcoded into the configuration and MySQL has not been tested. The psycopg2 driver is included in the requirements.txt file.

# Installation
    cd flare

Install the Python dependencies

    pip3 install -r requirements.txt

Install wkhtmltopdf for report support
    [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)
    
Install the modules needed by Svelte and build the frontend app

    cd svelte_client
    npm install
    npm run build
    
Create the apps and filestore directories

    mkdir apps
    mkdir filestore

# Usage (create and run an app)
Create a database e.g.

    CREATE DATABASE YourDbName OWNER YourUser;

Run the app creation script with the name of the app you want. This will scaffold the necessary structure for a new app, it will be created under the apps/ folder.

    ./new_app <yourappname>

The new app script also creates a dot file named the same as the app (copied from the .example file). This file contains the environment variables needed to run the app. Edit it to add the database information. Finally, run the server passing the app name as argument. The first time you run it, and on subsequent runs after more models are added or models are changed, peewee-db-evolve will generate the sql that needs to be executed in the database to match the defined models. If evolve is running on interactive mode type yes and enter. By default the server listens on port 6800.

    ./run.sh <yourappname>
    
# Docker
The included Dockerfile is based on an [image](https://github.com/tiangolo/meinheld-gunicorn-flask-docker) that runs flask apps behind meinheld and gunicorn. 

An optional PYTHON_REQUIREMENTS argument can be specified at build time (only neccesary if your app uses other python modules not included in the requirements.txt file, otherwise this argument defaults to requirements.txt).

    docker build --build-arg PYTHON_REQUIREMENTS=myrequirements.txt -t <imagename> ./
    
When running the image you must mount the apps/ and filestore/ folders, and you can remap the port if you want (the app runs on port 80 in the container). The configuration can be passed using the env_file argument.

    docker run -v ~/flare/apps:/app/apps -v ~/flare/filestore:/app/filestore --publish 6800:80 --env-file=.myenvfile <imagename>

# Built with
- [Peewee](http://docs.peewee-orm.com/en/latest/)
- [Svelte](https://svelte.dev/)
- [Flask](https://flask.palletsprojects.com/)

Work in progress. Documentation coming soon
