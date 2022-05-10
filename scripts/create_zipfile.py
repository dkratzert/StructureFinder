"""
Creates a zip file with the content of the StructureDB program.
"""
import shutil
import tempfile
from pathlib import Path
from zipfile import ZipFile

import os

from structurefinder.misc.version import VERSION
from structurefinder.searcher.misc import copy_file, remove_file, walkdir

version = VERSION

files = [
    "structurefinder",
    "cgi_ui",
    "icons"
    ]


def make_zip(filelist):
    """
    :type filelist: list
    """
    maindir = 'StructureFinder'
    tmpdir = tempfile.mkdtemp()
    fulldir = os.path.abspath(os.path.join(tmpdir, maindir))
    os.makedirs(fulldir)
    Path('./scripts/Output').mkdir(exist_ok=True)
    zipfilen = './scripts/Output/strf_cmd-v{}.zip'.format(version)
    remove_file(zipfilen)
    for f in filelist:
        for filen in walkdir(f, exclude=['.pyc']):
            path, _ = os.path.split(filen)
            target_dir = os.path.join(fulldir, path)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            print("Adding {}".format(filen))
            copy_file(filen, target_dir)
    with ZipFile(zipfilen, mode='w', allowZip64=False) as myzip:
        for filen in walkdir(maindir):
            myzip.write(filen)
    print("File written to {}".format(zipfilen))
    shutil.rmtree(tmpdir)

if __name__ == "__main__":
    make_zip(files)