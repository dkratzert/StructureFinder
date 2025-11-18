from __future__ import annotations

import os
import tarfile
import time
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Generator

import py7zr

DEBUG = False

EXCLUDED_NAMES = {'ROOT',
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
                  'autostructure_private'}


class FileType(Enum):
    CIF = 3
    RES = 4


suffix_to_type = {'.cif': FileType.CIF, '.res': FileType.RES}


@dataclass(frozen=True)
class Result:
    filename: str
    file_type: FileType
    file_path: str | bytes
    file_content: str
    archive_path: str | None = None
    modification_time: str = ''
    file_size: int = 0

    @property
    def in_archive(self) -> bool:
        return bool(self.archive_path)

    def __repr__(self):
        return f'Result: {self.filename} ({self.file_type}) in {self.file_path} \n{self.file_content[:160]}\n'


def is_excluded_dir(dirpath: str, exclude_dirs: Iterable[str]) -> bool:
    dirname = os.path.basename(dirpath)
    for ex in exclude_dirs:
        if dirname.lower() == ex:
            return True
    return False


def find_files(root_dir, exts=(".cif", ".res"), exclude_dirs=None, no_archive=False) -> Generator[Result | None, Any, None]:
    if exclude_dirs is None:
        exclude_dirs = set()
    exclude_dirs = set([x.lower() for x in exclude_dirs])
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if is_excluded_dir(dirpath, exclude_dirs):
            continue
        for num, filename in enumerate(filenames):
            lower_filename = filename.lower()
            if lower_filename.endswith('.sfrm'):
                continue
            filepath = os.path.normpath(os.path.join(dirpath, filename))
            if lower_filename.endswith(exts):
                yield from file_result(filename, filepath)
            elif no_archive:
                continue
            elif is_zipfile(lower_filename):
                yield from search_in_zip(filepath, exts, exclude_dirs)
            elif is_tarfile(lower_filename):
                yield from search_in_tar(filepath, exts)
            elif is_7z_file(lower_filename):
                yield from search_in_7z(filepath, exts)


def is_7z_file(filename: str) -> bool:
    return filename.endswith(".7z")


def is_tarfile(filename: str) -> bool:
    return filename.endswith(('*.tar.gz', '*.tar.bz2', '*.tgz'))


def is_zipfile(filename: str) -> bool:
    return filename.endswith(".zip")


def file_result(filename: str, filepath: str | bytes) -> Generator[Result | None, Any, None]:
    try:
        mod_time = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(filepath)))
        size = os.stat(filepath).st_size
    except FileNotFoundError:
        if DEBUG:
            print(f"File {filepath} not found.")
        return None
    with open(filepath, 'rb') as fobj:
        try:
            yield Result(file_type=suffix_to_type.get(filepath[-4:].lower()),
                         file_content=fobj.read().decode('latin1', 'replace'),
                         filename=filename, file_path=os.path.dirname(filepath),
                         modification_time=mod_time,
                         file_size=size)
        except OSError as e:
            print(f"OSError reading {filepath}:\n {e}")
            yield None


def search_in_zip(zip_path: str | bytes,
                  exts: tuple[str] | set[str],
                  exclude_dirs: Iterable[str] = None) -> Generator[Result | None, Any, None]:
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            for info, file in zip(archive.infolist(), archive.namelist()):
                filepath = os.path.basename(file)
                if is_excluded_dir(filepath, exclude_dirs):
                    continue
                lower_file = file.lower()
                if lower_file.endswith(exts):
                    with archive.open(file) as f:
                        yield Result(file_type=suffix_to_type.get(lower_file[-4:]),
                                     archive_path=zip_path,
                                     filename=file,
                                     file_content=f.read().decode('latin1', 'replace'),
                                     file_path=zip_path,
                                     modification_time=datetime(*info.date_time).strftime('%Y-%m-%d'))
    except Exception as e:
        if DEBUG:
            print(f"[ZIP] Error in {zip_path}: {e}")
    yield None


def search_in_tar(tar_path: str | bytes,
                  exts: tuple[str],
                  exclude_dirs: Iterable[str] = None) -> Generator[Result, Any, None]:
    try:
        with tarfile.open(tar_path, 'r:*') as archive:
            for file in archive.getmembers():
                if is_excluded_dir(file.name, exclude_dirs):
                    continue
                # file.name also has the path inside the archive in front:
                lower_file = file.name.lower()
                if lower_file.endswith(exts) and file.isfile():
                    f = archive.extractfile(file)
                    if f:
                        yield Result(file_type=suffix_to_type.get(lower_file[-4:]),
                                     archive_path=tar_path,
                                     filename=os.path.basename(file.name),
                                     file_content=f.read().decode('latin1', 'replace'),
                                     file_path=tar_path,
                                     file_size=file.size,
                                     modification_time=time.strftime('%Y-%m-%d', time.gmtime(file.mtime)))
    except Exception as e:
        if DEBUG:
            print(f"[TAR] Error in {tar_path}: {e}")


def search_in_7z(sevenz_path: str | bytes, exts: tuple[str]) -> Generator[Result, Any, None]:
    try:
        with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
            for entry in archive.list():
                name = entry.filename
                lower_file = name.lower()
                if lower_file.endswith(exts):
                    file_dict = archive.read([name])
                    bio = file_dict.get(name)
                    if bio:
                        yield Result(
                            file_type=suffix_to_type.get(lower_file[-4:]),
                            archive_path=sevenz_path,
                            filename=name,
                            file_content=bio.read().decode('latin1', 'replace'),
                            file_path=sevenz_path,
                            modification_time=entry.creationtime,
                            file_size=entry.uncompressed
                        )
    except Exception as e:
        if DEBUG:
            print(f"[7Z] Error in {sevenz_path}: {e}")


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    for num, result in enumerate(find_files(r"D:\\",
                                            exclude_dirs=EXCLUDED_NAMES)):
        print(result)
        print(num)
    # assert num == 254
