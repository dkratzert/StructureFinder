"""
Creates a zip file with the content of the StructureDB program.
"""
from zipfile import ZipFile

version = "1"

files = [
    "stdb_main.py",
    "stdb_cmd.py",
    "searcher/database_handler.py",
    "searcher/filecrawler.py",
    "searcher/fileparser.py",
    "searcher/misc.py",
    "searcher/searchhandler.py",
    "searcher/spinner.py",
    "searcher/strs.py",
    "searcher/__init__.py",
    "pymatgen/core/__init__.py",
    "pymatgen/core/mat_lattice.py",
    "pymatgen/util/__init__.py",
    "pymatgen/util/num_utils.py",
    "opengl/__init__.py",
    "opengl/moleculegl.py",
    "lattice/__init__.py",
    "lattice/lattice.py",
    "scripts/linux/stdb_cmd",
    "scripts/mac/stdb_cmd",
    "scripts/win/stdb_cmd.bat",
    "scripts/win/stdb.bat",
    ]


def make_zip(filelist):
    """
    :type filelist: list
    """
    with ZipFile('stdb-{}.zip'.format(version), 'w') as myzip:
        for f in filelist:
            print("Adding {}".format(f))
            myzip.write(f)


if __name__ == "__main__":
    make_zip(files)