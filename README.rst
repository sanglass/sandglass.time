=======================
Sandglass Documentation
=======================

Sandglass is a REST API based time tracking application.

It is based on the `Pyramid`_ web framework, and for ORM and data access it uses `SQLAlchemy`_.

See `notes`_.

.. _Pyramid: http://www.pylonsproject.org/
.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _notes: docs/source/notes.rst

Setting up after initial checkout
---------------------------------

.. code:: bash

  $ python setup.py develop
  $ cp sandglass-development.ini.dist sandglass.ini
  $ sandglass manage init-database
  $ sandglass manage create-user --admin
  $ pserve sandglass.ini

********
Frontend
********

Frontend implementation is being developed as a separate project called `sandglass-frontend`_.

.. _sandglass-frontend: https://github.com/gustavpursche/sandglass-frontend
