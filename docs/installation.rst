Installation
============

Windows
-------
The Windows version installs like any other Windows installer. You can download it from the
`StructureFinder homepage <https://dkratzert.de/structurefinder.html>`_.


Linux / Mac / Windows (Python Package)
---------------------------------------

Since version 73, there is a `PyPI <https://pypi.org/project/structurefinder>`_ package for
installation in a Python environment. StructureFinder requires **Python 3.12** or newer.

Do the following steps in order to install and run StructureFinder:

.. code-block:: bash

    python -m venv venv                                               # creates a virtual environment
    source venv/bin/activate   # Windows: venv\Scripts\activate.bat   # activates the environment
    pip install structurefinder
    strf                       # start the desktop GUI
    strf_cmd                   # or start the command-line indexer
    strf_web                   # or start the web interface

For subsequent starts, only activating the environment is necessary:

.. code-block:: bash

    source venv/bin/activate   # Windows: venv\Scripts\activate.bat
    strf

.. note::

   The command ``structurefinder`` is an alias for ``strf`` and also starts the
   desktop GUI.

Alternatively, you can use `uv <https://docs.astral.sh/uv/>`_ for faster
environment management:

.. code-block:: bash

    uv venv --python 3.12
    source .venv/bin/activate   # Windows: .venv\Scripts\activate.bat
    uv pip install structurefinder
    strf

