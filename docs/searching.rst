=========
Searching
=========

StructureFinder provides several ways to search for crystal structures in the
database.


Unit Cell Search
----------------

The cell search takes six parameters *a*, *b*, *c*, *α*, *β*, *γ*. The search
is unsharp, so ``10 10 10 90 90 90`` would find the same cell as
``10.00 10.00 10.00 90.00 90.00 90.00``.

The algorithm is a combination of a cell comparison by volume first (for speed)
and subsequent lattice matching. The lattice matching implementation is based on
the `pymatgen <http://pymatgen.org/>`_ project.

The tolerances for the cell search can be set directly in the main window with
the *Length tol.* and *Angle tol.* fields next to the search line. The length
tolerance is a relative value (0.03 means the cell edges may differ by 3 %) and
the angle tolerance is given in degrees. The same fields are available on the
*Advanced search* tab and both sets always show the same values.

The **More Results** check box only applies one of two presets to these fields:

**Regular** (unchecked)
    length: 0.03, angle: 1.0°

**More results** (checked)
    length: 0.08, angle: 1.8°

The values may be modified afterwards. On the main tab this repeats the search
immediately, on the advanced search tab the new values are used with the next
click on the *Search* button.

.. tip::

   Double-click on the unit cell display to copy the cell parameters to
   the clipboard.


Text Search
-----------

The text search field searches in the directory, file name, data name, and
.res file text data. You can use wildcards to build patterns:

- ``?`` matches a single character
- ``*`` matches any sequence of characters

For example, ``foo*bar`` means "foo[any text]bar".

The text search also covers author names from these CIF keys:

- ``_audit_author_name``
- ``_audit_contact_author_name``
- ``_publ_contact_author_name``
- ``_publ_contact_author``
- ``_publ_author_name``


Advanced Search
---------------

.. figure:: pics/strf_adv.png
   :width: 700

   Advanced search tab.

The "Advanced Search" tab allows you to search for several options at a time and
also allows to exclude parameters. Available search criteria include:

- Space group
- R1 value range
- Unit cell parameters
- Elements (inclusive and exclusive)
- CCDC number
- Crystal system
- Centering

Suggestions for additional search options are welcome.
