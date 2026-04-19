Command-Line Indexer
====================

With the ``strf_cmd`` command, you can index directories without a graphical
user interface. This is useful for scripted or automated indexing, for example
via a cron job.

The options ``-d`` and ``-e`` can be given multiple times, for example
``-d /foo -d /bar``.

.. code-block::

   $ strf_cmd
    usage: strf_cmd [-h] [-d "directory"] [-e "directory"]
                       [-o "sqlite file name"] [-c] [-r] [--delete]
                       [-f "unit cell"] [-m "sqlite file name"] [-na]

    Command line version 88 of StructureFinder to collect .cif/.res files to a
    database. StructureFinder will search for cif files in the given directory(s)
    recursively. (Either -c, -r or both options must be active!)

    options:
      -h, --help            show this help message and exit
      -d "directory"        Directory(s) where cif files are located.
      -e "directory"        Directory names to be excluded from the file search.
                            Default is: ['BrukerShelXlesaves',
                            'autostructure_private', '.OLEX', 'TEMP', 'ROOT',
                            'olex', '__private__', 'dsrsaves', 'shelXlesaves',
                            'Papierkorb', 'Recycle.Bin', 'TMP'] Modifying -e
                            option discards the default.
      -o "sqlite file name"
                            Name of the output database file. Default:
                            "./structuredb.sqlite" Also used for the commandline
                            search (-f option).
      -c                    Add .cif files (crystallographic information file) to
                            the database.
      -r                    Add SHELX .res files to the database.
      --delete              Delete and do not append to previous database.
      -f "unit cell"        Search for the specified unit cell. The cell values
                            have to be enclosed in brackets.
      -m "sqlite file name"
                            Merges a database file into the file of '-o' option.
                            Only -o is allowed in addition.
      -na                   Disables the collection of files in .zip, .tar.gz,
                            .tar.bz2, .tgz, .7z archives.


Indexing Example
----------------

The following example indexes all .cif and .res files in a directory and creates
the file ``structuredb.sqlite`` in the current directory:

.. code-block:: bash

    $ strf_cmd -d /path/to/structures -c -r

.. code-block::

    Collecting .res and .cif files below /path/to/structures.

    Added 253 files, (249 .cif, 4 .res files), (209 in compressed archives) to database in:  0 h,  0 m, 0.87 s
    ---------------------
    Total 253 cif/res files in '/path/to/structures/structuredb.sqlite'.


The command-line version always appends all data to an already existing database
in the current working directory. Use the ``--delete`` option to start fresh.


Unit Cell Search
----------------

You can also search for a unit cell from the command line:

.. code-block:: bash

    $ strf_cmd -f "10.5086 20.9035 20.5072 90.000 94.130 90.000"


Database Merging
----------------

To merge one database into another:

.. code-block:: bash

    $ strf_cmd -m source.sqlite -o target.sqlite
