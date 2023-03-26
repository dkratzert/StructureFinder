Command Line file Indexer
=========================

With the strf_cmd command, you can index directories without a graphical
user interface.

The options -d and -e can be given multiple times like -d /foo -d /bar.

.. code-block::

   $ strf_cmd
   usage: strf_cmd.py [-h] [-d "directory"] [-e "directory"] [-o "file name"]
   Command line version of StructureFinder to collect cif files to a database.
   StructureFinder will search for cif/res files in the given directory(s)
   recursively. (Either -c, -r or both options must be active!)
   optional arguments:
     -h, --help            show this help message and exit
     -d "directory"        Directory(s) where cif files are located.
     -e "directory"        Directory names to be excluded from the file search. Default is: "ROOT", ".OLEX", "TMP", "TEMP", "Papierkorb", "Recycle.Bin" Modifying -e option
                           discards the default.
     -o "sqlite file name"
                           Name of the output database file. Default: "./structuredb.sqlite" Also used for the commandline search (-f option).
     -c                    Add .cif files (crystallographic information file) to the database.
     -r                    Add SHELX .res files to the database.
     --delete              Delete and do not append to previous database.
     -f CELL               Search for the specified unit cell. The cell values have to be enclosed in brackets.
     -m MERGE              Merges a database file into the file of '-o' option.
