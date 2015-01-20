cses.py
=======

A command line client for `cses.fi`_

Currently very incomplete. All of the commands can be abbreviated as long as
there is no collision.

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
       submits the current FILE to the server and prints the response

.. _cses.fi: http://cses.fi/
