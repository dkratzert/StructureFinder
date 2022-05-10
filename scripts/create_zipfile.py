"""
Creates a zip file with the content of the StructureDB program.
"""
import os
import tempfile
from pathlib import Path
from zipfile import ZipFile

from structurefinder.misc.version import VERSION
from structurefinder.searcher.misc import remove_file

version = VERSION

filelist = [
    "structurefinder",
    "cgi_ui",
    "icons",
    'strf_cmd.bat',
    'strf_cmd',
    'requirements-cmd.txt'
]

excludes = ['.pyc', ]


def is_valid(file: Path):
    status = True
    if file.parts[0] not in filelist:
        status = False
    if file.suffix in excludes:
        status = False
    if file.parts[-1] == '__pycache__':
        status = False
    if file.name == 'strf.py':
        status = False
    return status

def make_zip():
    maindir = 'StructureFinder'
    tmpdir = tempfile.mkdtemp()
    fulldir = os.path.abspath(os.path.join(tmpdir, maindir))
    os.makedirs(fulldir)
    Path('./scripts/Output').mkdir(exist_ok=True)
    zipfilen = './scripts/Output/strf_cmd-v{}.zip'.format(version)
    remove_file(zipfilen)
    with ZipFile(zipfilen, mode='w', allowZip64=False) as myzip:
        for file in Path('.').parent.parent.rglob('*'):
            if not is_valid(file):
                continue
            print(f"Adding file: {file}")
            myzip.write(file)
    print("File written to {}".format(zipfilen))


if __name__ == "__main__":
    make_zip()
