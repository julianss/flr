# Flare
Framework for creating business web applications. Basically, it's a fully functioning app in which you just define your own models and business logic.

It was inspired by [Odoo](https://odoo.com).

- Back-end: Python (Flask and Peewee)
- Front-end: Svelte

# Dependencies
- python at least 3.5.2
- node 14

# Database support
Although Peewee supports more than PostgreSQL and MySQL, automatic migrations are provided by peewee-db-evolve, which supports only those two. For now, though, PostgreSQL is hardcoded into the configuration. Driver installation:

    pip3 install psycopg2-binary==2.8.6

# Installation
    cd flare

Install the Python dependencies

    pip3 install -r requirements.txt

Install wkhtmltopdf for report support
    [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)
    
Install svelte

    cd svelte_client
    npm install

Make the new_app script executable

    chmod a+x new_app

Create the apps directory, here is where new apps will be created

    mkdir apps

# Usage (create and run an app)
Create a database e.g.

    CREATE DATABASE YourDbName OWNER YourUser with PASSWORD

Run the app creation script with the name of the app you want. A new folder will be created in the "apps" folder with that name

    ./new_app YourAppName

The new app script also creates a dot file in the flare/ folder named **.YourAppName**. Edit it to add the database information. Finally run the server passing the app name as argument. The first time you run it, and on subsequent runs after more models are added, peewee-db-evolve will generate the sql that needs to be executed in the database to match the defined models, type yes and enter. By default the server listens on port 6800.

    python3 run.py YourAppName

# Built with
- [Peewee](http://docs.peewee-orm.com/en/latest/)
- [Svelte](https://svelte.dev/)
- [Flask](https://flask.palletsprojects.com/)


Work in progress.
