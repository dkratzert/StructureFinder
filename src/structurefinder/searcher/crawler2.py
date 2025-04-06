from __future__ import annotations

import os
import tarfile
import zipfile
from collections.abc import Iterable, Callable
from dataclasses import dataclass
from enum import Enum

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
    modification_time: int = 0
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


def find_files(root_dir, exts=(".cif", ".res"), exclude_dirs=None, progress_callback: Callable = None):
    if exclude_dirs is None:
        exclude_dirs = set()
    exclude_dirs = set([x.lower() for x in exclude_dirs])

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if is_excluded_dir(dirpath, exclude_dirs):
            continue
        total = len(filenames)
        for num, filename in enumerate(filenames):
            if progress_callback:
                progress_callback(int((num + 1) / total * 100))

            if filename.lower().endswith(exts):
                filepath = os.path.join(dirpath, filename)
                yield from file_result(filename, filepath)
            elif is_zipfile(filename):
                filepath = os.path.join(dirpath, filename)
                yield from search_in_zip(filepath, exts, exclude_dirs)
            elif is_tarfile(filename):
                print('TODO: Implement tar indexing')
                continue
                filepath = os.path.join(dirpath, filename)
                yield from search_in_tar(filepath, exts)
            elif filename.endswith(".7z"):
                filepath = os.path.join(dirpath, filename)
                yield from search_in_7z(filepath, exts)


def is_tarfile(filename: str) -> bool:
    if filename.lower().endswith(".tar.gz"):
        return True
    return False


def is_zipfile(filename: str) -> bool:
    if filename.lower().endswith(".zip"):
        return True
    return False


def file_result(filename, filepath):
    with open(filepath, 'rb') as fobj:
        yield Result(file_type=suffix_to_type.get(filepath.lower()[-4:]),
                     file_content=fobj.read().decode('latin1', 'replace'),
                     filename=filename, file_path=filepath)


def search_in_zip(zip_path: str, exts: tuple[str] | set[str], exclude_dirs: Iterable[str] = None):
    try:
        with zipfile.ZipFile(zip_path, 'r') as archive:
            for file in archive.namelist():
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
                                     file_path=file)
    except Exception as e:
        print(f"[ZIP] Error in {zip_path}: {e}")
        # raise


def search_in_tar(tar_path: str, exts: Iterable[str], exclude_dirs: Iterable[str] = None):
    try:
        with tarfile.open(tar_path, 'r:*') as archive:
            for member in archive.getmembers():
                if member.name.lower().endswith(exts) and member.isfile():
                    f = archive.extractfile(member)
                    if f:
                        yield Result("tar", tar_path, member.name, f.read())
    except Exception as e:
        print(f"[TAR] Error in {tar_path}: {e}")


def search_in_7z(sevenz_path: str, exts: Iterable[str], exclude_dirs: Iterable[str] = None):
    try:
        with py7zr.SevenZipFile(sevenz_path, mode='r') as archive:
            for name, bio in archive.readall().items():
                if name.lower().endswith(exts):
                    yield ("7z", sevenz_path, name, bio.read())
    except Exception as e:
        print(f"[7Z] Error in {sevenz_path}: {e}")


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    for num, result in enumerate(
        find_files("/Users/daniel/Documents/GitHub/StructureFinder", exclude_dirs=EXCLUDED_NAMES)):
        print(result)
    print(num)
    assert num == 254
