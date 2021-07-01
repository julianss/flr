Getting Started
===============

Installation
--------------------------
Download flr and install its Python dependencies, which are provided in the requirements.txt file.

.. code-block:: text

    pip3 install -r requirements.txt 

Run the example app
--------------------------
flr is configured through environment variables. This configuration consists of, among other things,
the name of the app to run (which corresponds to the name of the folder which the app's files are),
and the parameters to connect to a PostgresQL database. Edit the .example file to provide the
necessary credentials to a PostgreSQL instance. 

.. code-block:: text

    flr_db_host=
    flr_db_user=
    flr_db_pass=
    flr_db_name=

Run the server by executing the run script and the name of the app.

.. code-block:: text

    ./run.sh example

You should now be prompted with a bunch of SQL commands. Type "yes" and enter. This will create the
database tables. When it's done point your browser to localhost:6800 to open the app. You will see
the login screen. The default user is admin, and the password is also admin (this password can be
changed through the configuration variables). Once logged in you can interact with the web client.

Web client overview
--------------------------
Menus and views
````````````````````
The web client consists of sections, menus and views. A section is each different link that appears
in the topbar. When clicked, a section displays a dropdown menu of options. Each of this options is
called a menu, and each menu opens a different view or group of views. Views come in different flavors:

List view
^^^^^^^^^^^^^
The list view shows a list of paged records. It can be filtered to show only records that satisfy
certain criteria. Records can be selected in order to execute batch actions on them. New records
may be created using the New button, this will open a blank form.

Card view
^^^^^^^^^^^^^
Like the list view, but instead of rendering each record as a row in a table, it renders them using
a custom html template.

Search view
^^^^^^^^^^^^^
This is a dialog used to filter the list and card view, where values and conditions for each field
can be specified.

Form view
^^^^^^^^^^^^^
When a row in the List view is clicked, the form view is displayed. The form view shows a record
in detail. From here the edit mode can be activated wherein the fields become editable and the
record can be updated. The Form view renders each field according to its type. Hence it will render
Date fields as a date input, Boolean fields as a checkbox and so on. New records can be created,too.
To create a new record press the New button, the form will go blank so new information can be entered.
