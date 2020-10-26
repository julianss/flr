# Fla:RE
Framework for creating business web applications

Powered by Flask and Svelte (hence **FLA**sk & **RE**active), and inspired by the engine behind Odoo (once known as the OpenObject framework). Uses Peewee as the ORM.

# Dependencies
- python at least 3.5.2
- node 14

# Database setup
Since Peewee supports several databases, install the python driver of your choice. For example for Postgresql:

    pip3 install psycopg2-binary==2.8.6

# Installation
    cd flare
    
Install the Python dependencies

    pip3 install -r requirements.txt
    
Make the new_app script executable

    chmod a+x new_app
    
Create the apps directory, here is where new apps will be created

    mkdir apps

# Usage (create and run an app)
Create a database e.g.

    CREATE DATABASE YourDbName OWNER YourUser with PASSWORD
    
Run the app creation script with the name of the app you want. A new folder will be created in the apps folder with that name, and the svelte project will be created. Install the npm modules and build the client.

    ./new_app YourAppName
    cd apps/YourAppName/client
    npm install
    npm run build
    
Download a bootstrap.min.css in the public/ folder of the client. You can download one from [Bootswatch](https://bootswatch.com/)

The new app script also creates a dot file in the flare/ folder named **.YourAppName**. Edit it to add the database information. Insert a random string in the JWT Secret variable. Set interactive evolve and flask debug to "True". Finally run the server passing the app name as argument. The first time you run it (and on subsecuent runs after more models area created) peewee-db-evolve will present you with the sql that needs to be executed in the database, type yes and enter. By default the server listens on port 6800.

    ṕython3 run.py YourAppName

# Built with
- [Peewee](http://docs.peewee-orm.com/en/latest/)
- [Svelte](https://svelte.dev/)
- [Flask](https://flask.palletsprojects.com/)


Work in progress.
