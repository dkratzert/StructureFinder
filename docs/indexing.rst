Indexing Files
==============

The "Import Directory" button starts indexing of .cif or .res files below the
selected directory recursively, depending on which file ending is enabled.

StructureFinder scans all subdirectories for .cif/.res files as well as
compressed archives containing .cif files. The following archive formats are
supported:

- .zip
- .tar.gz / .tgz
- .tar.bz2
- .7z

The time for indexing mostly depends on the speed of your hard drive.
Scanning a complete 256 GB SSD takes about 50 seconds. A ten-year-old file
server with over 100 user directories and 20,000 crystal structures can take
about an hour.

.. note::

   Indexing on a network drive can be very slow.

Indexing runs in the background and does not block the GUI, so you can continue
to use the application while it is working. Indexing can be aborted at any time.

The following directory names are excluded from indexing by default:

- ``ROOT``
- ``.OLEX``
- ``olex``
- ``TMP``
- ``TEMP``
- ``Papierkorb``
- ``Recycle.Bin``
- ``dsrsaves``
- ``BrukerShelXlesaves``
- ``shelXlesaves``
- ``__private__``
- ``autostructure_private``

To append additional directories to an existing database, use the "Append
Directory" button.
