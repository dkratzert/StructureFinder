

Indexing Example
================

Creates the file structuredb.sqlite in the current directory:

.. code-block::

   ./strf_cmd -d D:\Github\StructureFinder -o test.sqlite -c -r --delete

    collecting *.cif, *.zip, *.tar.gz, *.tar.bz2, *.tgz, *.res files below .
      49 files considered.
    Added 255 files (251 cif, 4 res) files (212 in compressed files) to database in:  0 h,  0 m, 2.31 s
    ---------------------

    Total 255 cif/res files in '/Users/daniel/Documents/GitHub/StructureFinder/test.sqlite'.
    Duration:  0 h,  0 m, 2.33 s

The command line version always appends all data to an already existing database in the current working directory.
It will not append the date with the --delete option.
