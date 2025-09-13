import time

from PyQt6.QtCore import QObject, pyqtSignal

from structurefinder.searcher.crawler import EXCLUDED_NAMES, FileType, find_files
from structurefinder.searcher.database_handler import StructureTable
from structurefinder.strf_cmd import process_cif, process_res


class SearchWorker(QObject):
    progress = pyqtSignal(int)
    number_of_files = pyqtSignal(int)
    finished = pyqtSignal()

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

    def stop(self):
        self._stop = True
        print('Stopping index worker...')

    def run(self):
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
            if result.file_type == FileType.CIF:
                if process_cif(lastid, result, self.structures):
                    lastid += 1
            if result.file_type == FileType.RES:
                if process_res(lastid, result, self.structures):
                    lastid += 1
            self.progress.emit(num)
        self.progress.emit(0)
        self.finished.emit()
        t2 = time.perf_counter()
        print(f'Finished index worker at {t2 - t1:.2f} seconds')
