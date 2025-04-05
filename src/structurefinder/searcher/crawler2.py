from __future__ import annotations

import os
import sys
import tarfile
import zipfile
from dataclasses import dataclass
from enum import Enum

EXCLUDED_NAMES = ('ROOT',
                  '.OLEX',
                  'olex',
                  'TMP',
                  'TEMP',
                  'Papierkorb',
                  'Recycle.Bin',
                  'dsrsaves',
                  'BrukerShelXlesaves',
                  'shelXlesaves',
                  '__private__',
                  'autostructure_private')


class FileType(Enum):
    FILE = 1
    ARCHIVE = 2


@dataclass(frozen=True)
class Result:
    filename: str
    file_type: FileType
    file_path: str | bytes
    file_content: str
    archive_path: str | None = None

    def __repr__(self):
        return f'Result: {self.filename} ({self.file_type}) in {self.file_path} \n{self.file_content[:160]}\n'


def find_files(root_dir, exts=(".cif", ".res"), exclude_dirs=None, progress_callback=None):
    if exclude_dirs is None:
        exclude_dirs = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames
                       if not is_excluded(os.path.join(dirpath, d), exclude_dirs)]
        total = len(filenames)
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if is_excluded(filepath, exclude_dirs):
                continue
            if progress_callback:
                progress_callback(int((i + 1) / total * 100))

            if filename.lower().endswith(exts):
                yield from file_result(filename, filepath)
            elif zipfile.is_zipfile(filepath):
                yield from search_in_zip(filepath, exts)
            elif tarfile.is_tarfile(filepath):
                yield from search_in_tar(filepath, exts)
            elif filename.lower().endswith(".7z"):
                yield from search_in_7z(filepath, exts)


def file_result(filename, filepath):
    with open(filepath, 'rb') as fobj:
        yield Result(file_type=FileType.FILE,
                     file_content=fobj.read().decode('latin1', 'replace'),
                     filename=filename, file_path=filepath)


def is_excluded(path, exclude_dirs):
    path = os.path.abspath(path)
    for ex in exclude_dirs:
        ex = os.path.abspath(ex)
        if os.path.commonpath([path, ex]) == ex:
            return True
    return False


def is_internal_excluded(internal_path, exclude_dirs):
    if exclude_dirs is None:
        return False
    for ex in exclude_dirs:
        ex = ex.replace("\\", "/").rstrip("/") + "/"
        if internal_path.startswith(ex):
            return True
    return False


def search_in_zip(zip_path, exts, exclude_dirs=None):
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            for file in archive.namelist():
                norm_path = file.replace("\\", "/")  # falls Windows ZIPs
                if is_internal_excluded(norm_path, exclude_dirs):
                    continue
                if norm_path.lower().endswith(exts):
                    with archive.open(file) as f:
                        yield Result(file_type=FileType.ARCHIVE,
                                     archive_path=zip_path,
                                     filename=file,
                                     file_content=f.read().decode('latin1', 'replace'),
                                     file_path=file)
    except Exception as e:
        print(f"[ZIP] Error in {zip_path}: {e}")


def search_in_tar(tar_path, exts):
    try:
        with tarfile.open(tar_path, 'r:*') as archive:
            for member in archive.getmembers():
                if member.name.lower().endswith(exts) and member.isfile():
                    f = archive.extractfile(member)
                    if f:
                        yield ("tar", tar_path, member.name, f.read())
    except Exception as e:
        print(f"[TAR] Error in {tar_path}: {e}")


def search_in_7z(sevenz_path, exts):
    try:
        with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
            for name, bio in archive.readall().items():
                if name.lower().endswith(exts):
                    yield ("7z", sevenz_path, name, bio.read())
    except Exception as e:
        print(f"[7Z] Error in {sevenz_path}: {e}")


if __name__ == '__main__':
    #app = QApplication(sys.argv)
    for result in find_files("/Users/daniel/Documents/GitHub/StructureFinder", exclude_dirs=EXCLUDED_NAMES):
        print(result)
