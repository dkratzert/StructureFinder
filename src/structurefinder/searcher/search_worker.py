import sqlite3
import time

from qtpy.QtCore import QObject, Signal

from structurefinder.searcher.crawler import EXCLUDED_NAMES, FileType, find_files
from structurefinder.searcher.database_handler import StructureTable
from structurefinder.strf_cmd import process_cif, process_res


class SearchWorker(QObject):
    progress = Signal(int)
    number_of_files = Signal(int)
    finished = Signal()

    def __init__(self,
                 root_dir: str,
                 structures_db: StructureTable,
                 add_res: bool,
                 add_cif: bool,
                 no_archives: bool = False) -> None:
        super().__init__()
        self.add_res = add_res
        self.add_cif = add_cif
        self.no_archives = no_archives
        self._stop = False
        self.root_dir = root_dir
        self.exclude_dirs = EXCLUDED_NAMES
        self.structures = structures_db

    def stop(self) -> None:
        self._stop = True
        print('Stopping index worker...')

    def run(self) -> None:
        t1 = time.perf_counter()
        exts = ('.cif', '.res')
        if self.add_res and not self.add_cif:
            exts = ('.res',)
        elif self.add_cif and not self.add_res:
            exts = ('.cif',)
        lastid = self.structures.database.get_lastrowid()
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        for num, result in enumerate(find_files(self.root_dir, exclude_dirs=EXCLUDED_NAMES,
                                                exts=exts, no_archive=self.no_archives)):
            if self._stop:
                break
            try:
                if result.file_type == FileType.CIF:
                    if process_cif(lastid, result, self.structures):
                        lastid += 1
                if result.file_type == FileType.RES:
                    if process_res(lastid, result, self.structures):
                        lastid += 1
            except sqlite3.IntegrityError:
                # This prevents problems with not-counted lastids from half-indexed files.
                continue
            except Exception:
                print(f'Error processing file {result.filename}')
                import traceback
                traceback.print_exc()
                continue
            self.progress.emit(num)
        self.progress.emit(0)
        self.finished.emit()
        t2 = time.perf_counter()
        print(f'Finished index worker at {t2 - t1:.2f} seconds')
