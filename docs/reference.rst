Reference
=============
(work in progress)

Configuration
-------------------------

These are the environment variables used to configure the app

``flr_app``

This is the name of the app, i.e. the name of the subdirectory of ``app/`` that
contains the app's files.

``flr_app_title``

Human-friendly app title . This string will be used as the title of the page (i.e.
the name that shows in the browser tab).

``flr_db_name``

The PostgreSQL database name. If it doesn't exist at startup time, its creation will be attempted.

``flr_db_user``

The name of the PostgreSQL database user.

``flr_db_pass``

The password for the PostgreSQL database user.

``flr_db_host``

The PostgreSQL database host.

``flr_db_port``

The PostgreSQL database port. The ``new_app`` script writes 5432 for you when creating the dot file
but change it if needed. Don't leave it blank, though.

``flr_db_interactive_evolve``

True/False. Whether to show an interactive prompt for confirmation when making changes to the
database schema. If set to False, each time the server is started, if the schema needs
updating, the changes will be automatically made without asking. It is advised to set this
to True during development and to False when in production.

``flr_flask_debug``

True/False. Whether to run Flask in debug mode or not

``flr_jwt_secret``

Place here a random string of characters, this will be the secret used to decode the jwt token used
for authentication (the ``new_app`` script automatically generates a random string here).

``flr_admin_pass``

Password for logging in as the superuser (admin). Note that this value is always read each time
the server is started. If you changed the admin password in any other way it will be overwritten.

``flr_mail_host``

SMTP host for sending mail.

``flr_mail_port``

SMTP host port

``flr_mail_user``

User to login into the SMTP server

``flr_mail_pass``

Password to login into the SMTP server

``flr_legacy_table_names``

True/False. Whether to turn on/off Peewee's ``legacy_table_names`` option.