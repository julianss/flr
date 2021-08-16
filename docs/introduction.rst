Introduction
============
What is flr?
-----------------------

flr is a system for creating BREAD (browse-read-edit-add-delete) web applications very quickly.
Basically, it's a fully functioning "blank" application where you just define the business logic and the layout of
the views and menus, and put your colors and logos.

flr consists of a backend service (written in Python using the `Flask`_ framework and the
`Peewee`_ ORM), and a frontend GUI  which consumes that service (made with `Svelte`_). Of course,
the backend can also be used on its own and you can build any other client to consume it.

flr was inspired by the engine that powers the `Odoo`_ apps.
Many ideas are taken from there but this is not an Odoo fork, it is a
re-imagining coded from scratch. 

.. _Flask: https://www.palletsprojects.com/p/flask/
.. _Peewee: https://github.com/coleifer/peewee
.. _Svelte: https://svelte.dev/
.. _Odoo: https://www.odoo.com


Is this a code-generating solution?
------------------------------------
No, flr does not generate any code. It is not based on a REST API
where there are a gazillion routes (typically at least one for each entity).
Instead it uses a RPC paradigm, where there is basically just one endpoint
for communicating directly with the business models. This means that you
you don't have to write any controllers. Just models and their methods. 

For the frontend you don't have to write any JS or HTML. Just define the views (using JSON files)
and the dynamic components will render everything for you.


What does the name flr mean?
----------------------------------
flr was originally going to be called Flare (it's just a name that starts with the same
two letters as Flask, the underlying web framework). But since there are already
a couple projects or services called Flare or that have Flare in their name, it was
renamed to flr. This can be still pronounced "flare", or pronounced by saying each letter
one by one (F-L-R).
