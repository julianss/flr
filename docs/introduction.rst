Introduction
============
What is flr?
-----------------------

flr is a system for creating CRUD/admin/enterprise applications very quickly.
It is "blank" web application in which you just have to insert the business logic.

flr consists of a backend service (written in Python using the Flask framework and the
Peewee ORM), and a frontend GUI  which consumes that service (made with Svelte). Of course,
the backend can also be used on its own and you can build any other client to consume it.

Is this a code-generating solution?
------------------------------------
No, flr does not generate any code. It is not based on a REST API
where there are a gazillion routes (typically at least one for each entity).
Instead it uses a RPC paradigm, where there is basically just one endpoint
for communicating directly with the business models. This means that for the backend
you don't have to write any controllers. Just models and their methods. And for the
frontend you don't have to write any JS or HTML. Just define the views (using JSON files)
and they will be dynamically rendered at runtime.


Inspiration
-----------------------------
flr is inspired, on one hand, by the engine that powers the `Odoo`_ apps.
Many ideas are taken from there but this is not an Odoo fork, it is a
re-imagining coded from scratch. On the other hand it also takes some inspiration
from web2py, in that it is a system that tries to provide an all-in-one solution
for a lot of common features of web applications.

.. _Odoo: https://www.odoo.com

What does the name flr mean?
----------------------------------
flr was originally going to be called Flare (it's just a name that starts with the same
two letters as Flask, the underlying web framework). But since there are already
a couple projects or services called Flare or that have Flare in their name, so it was
renamed to flr. This can be still pronounced "flare", or pronounced by saying each letter
one by one (F-L-R).
