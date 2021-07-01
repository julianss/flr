Introduction
============
What is flr?
-----------------------

flr is a system for creating "admin" or "enterprise" applications very quickly.
It is a generic web application in which you just have to insert the business logic.
This means that all applications made with flr look "the same" (custom CSS styles aside)
and have the same basic functionalities, and only the data models are different. 

flr consists of a backend service (written in Python using the Flask framework and the
Peewee ORM), and a client which consumes that service (made with Svelte). Of course,
the backend can also be used on its own and you can build any other client to consume it.

Inspiration
-----------------------------
flr is inspired, on one hand, by Odoo, an open source ERP. Many ideas are taken from there
but this is not an Odoo fork, it is a re-imagining coded from scratch. On the other hand it
also takes some inspiration from web2py, in that it is a system that tries to provide an
all-in-one solution for a lot of common tasks.

What does the name flr mean?
----------------------------------
flr was originally going to be called Flare (it's just a name that starts with the same
two letters as Flask, the underlying web framework). Nevertheless, apparently there already
a lot of projects or services called Flare or that have Flare in their name, so it was
renamed to flr. This can be still pronounced "flare", or pronounced by saying each letter
one by one (F-L-R).
