Installation
============

Windows
-------
The windows version installs like any other Windows installer.

Linux / Mac / Windows
---------------------
Since version 73, there is a `pypi <https://pypi.org/project/structurefinder>`_ package for installation in a Python environment.
Do the following steps in order to install and run StructureFinder in any Python environment:

.. code-block::

    >> python -m venv venv        <-- creates a virtual environment
    >> source venv/bin/activate   (Windows: venv\Scripts\activate.bat)  <-- Activates the environment
    >> pip install structurefinder
    >> strf  or strf_cmd  or  strf_web

For the next start, only

.. code-block::

    >> source venv/bin/activate   (Windows: venv\Scripts\activate.bat)
    >> strf  or strf_cmd  or  strf_web

is necessary.

