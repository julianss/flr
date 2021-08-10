Reference
=============

Fields
-------


Configuration variables
-------------------------

These are all the environment variables used to configure the app

``flr_app``

This is the name of the app, i.e. the name of the subdirectory of ``app/`` that
contains the app's files.

``flr_app_title``

Human-friendly app title . This string will be used as the title of the page (i.e.
the name that shows in the browser tab).

``flr_db_name``

The database name. If it doesn't exist at startup time, its creation will be attempted.

``flr_db_user``

The name of the database user.

``flr_db_pass``

The password for the database user.

``flr_db_host``

The database host.

``flr_db_port``

The database port. Must be neccesarily specified, as it does not assume a default value.

``flr_db_interactive_evolve``

True/False. Whether to show an interactive prompt for confirmation when making changes to the
database schema. If set to False, each time the server is started, if the schema needs
updating, the changes will be automatically made without asking. It is advised to set this
to True during development and to False when in production.

``flr_flask_debug``

True/False. Whether to run Flask

``flr_jwt_secret``
``flr_auth_field``
``flr_admin_pass``
``flr_mail_host``
``flr_mail_port``
``flr_mail_user``
``flr_mail_pass``
``flr_legacy_table_names``
``flr_send_error_btn``