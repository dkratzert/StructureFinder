"""
Creates a zip file with the content of the StructureDB program.
"""
import os
import tempfile
from pathlib import Path
from zipfile import ZipFile

from structurefinder.misc.version import VERSION

version = VERSION

filelist = [
    "structurefinder",
    "cgi_ui",
    "icons",
    'strf_cmd.bat',
    'strf_cmd',
    'strf_web',
    'requirements-cmd.txt',
    'install_min_requirements',
    'install_all_requirements',
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
    Path(zipfilen).unlink(missing_ok=True)
    with ZipFile(zipfilen, mode='w', allowZip64=False) as myzip:
        for file in Path('.').parent.parent.rglob('*'):
            if not is_valid(file):
                continue
            print(f"Adding file: {file}")
            myzip.write(file)
    print("File written to {}".format(zipfilen))


if __name__ == "__main__":
    make_zip()
