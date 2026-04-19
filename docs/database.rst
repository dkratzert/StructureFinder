Database Format
===============

The database format is plain `SQLite <http://www.sqlite.org/>`_.
You can view the database structure with tools like
`DB Browser for SQLite <https://sqlitebrowser.org/>`_.

The default database file name is ``structuredb.sqlite``.


Database Merging
----------------

Two databases can be merged into one using the ``-m`` option of ``strf_cmd``:

.. code-block:: bash

   strf_cmd -m source.sqlite -o target.sqlite

This is useful for combining databases created from different directories or on
different machines.
