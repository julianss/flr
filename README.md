# Fla:RE
Framework for creating business web applications

Powered by Flask and Svelte (hence **FLA**sk & **RE**active), and inspired by Odoo (formerly known as OpenObject framework).

# Dependencies
- python 3.5.2
- node 14

# Backend

    - Posgresql
        - postgresql 9.5.23
        - pip3 install psycopg2-binary==2.8.6

## Helps
    If npm installed try:
        - npm cache clean -f
        - npm install -g n
        - sudo n 14

# Installation
- cd flare
- pip3 install -r requirements.txt
- chmod a+x new_app
- mkdir apps

# Usage
- Postgresql
    - CREATE DATABASE **YourAppName** OWNER YourUser (with PASSWORD).
- Run ./new_app **YourAppName** same as your database.
- cd apps/**YourAppName**/client
- npm install
- npm run dev
- new terminal into /flare
- python3 run.py **YourAppName**

# Building with
- [Peewee](http://docs.peewee-orm.com/en/latest/)
- [Svelte](https://svelte.dev/)
- [Flask](https://flask.palletsprojects.com/)


Work in progress.