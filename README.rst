cses.py
=======

A command line client for `cses.fi`_

Installing
----------

Clone the repo, start a virtualenv and ``./setup.py install``. Or if you don't
do virtualenvs just ``sudo ./setup.py install``. Currently tested only only on
``Python 3.4`` on Linux, but should work with at least ``Python 3.2`` too.

Using
-----

First ``cses conf`` to set your credentials. Then ``cses task select`` to select
a course and a task. If you already have some code, you can use ``cses assoc``
to associate it with the selected task. If you would like a new file, use
``cses create``. To edit your selected file you can use ``cses edit`` and to
view the description of the task in your browser you can use ``cses show``.
Finally, to submit your code for evaluation, you can use ``cses submit``.

Commands
--------

All of the commands can be abbreviated as long as there is no collision.

.. code::

   cses conf
       set your username and password

   cses course show
       show all courses
   cses course select
       select your course

   cses task show
       show all tasks in the currently selected course
   cses task select
       select your task

   cses next
       go to the next task
   cses previous
       go to the previous task

   cses associate FILE
       associates the FILE with the current task
   cses submit
       submits the current task to the server and prints the response
   cses create
       creates a file for the task
   cses edit
       edits the current tasks file with your default editor ($EDITOR)
   cses show
       shows the current tasks description in your browser

.. _cses.fi: http://cses.fi/
