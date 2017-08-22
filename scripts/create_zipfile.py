"""
Creates a zip file with the content of the StructureDB program.
"""
from zipfile import ZipFile

import os

from strf import VERSION

version = VERSION

files = [
    "strf.py",
    "strf_cmd.py",
    "apex/__init__.py",
    "apex/apeximporter.py",
    "searcher/__init__.py",
    "searcher/atoms.py",
    "searcher/constants.py",
    "searcher/database_handler.py",
    "searcher/elements.py",
    "searcher/filecrawler.py",
    "searcher/fileparser.py",
    "searcher/misc.py",
    "searcher/spinner.py",
    "pymatgen/__init__.py",
    "pymatgen/core/__init__.py",
    "pymatgen/core/mat_lattice.py",
    "pymatgen/util/__init__.py",
    "pymatgen/util/num_utils.py",
    "lattice/__init__.py",
    "lattice/lattice.py",
    "pg8000/__init__.py",
    "pg8000/_version.py",
    "pg8000/core.py",
    ]


def make_zip(filelist):
    """
    :type filelist: list
    """
    os.chdir('../')
    with ZipFile('strf_cmd-v{}.zip'.format(version), 'w') as myzip:
        for f in filelist:
            print("Adding {}".format(f))
            myzip.write("StructureFinder/"+f)


if __name__ == "__main__":
    make_zip(files)