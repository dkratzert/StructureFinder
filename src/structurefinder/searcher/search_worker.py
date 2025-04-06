from PyQt5.QtCore import QObject, QThread, pyqtSignal

from structurefinder.searcher.crawler2 import Result, FileType, find_files, EXCLUDED_NAMES
from structurefinder.searcher.database_handler import StructureTable
from structurefinder.strf_cmd import get_database, process_cif, process_res


class SearchWorker(QObject):
    progress = pyqtSignal(int)
    found = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, root_dir: str, structures_db: StructureTable) -> None:
        super().__init__()
        self.stop = False
        self.root_dir = root_dir
        self.exclude_dirs = EXCLUDED_NAMES
        self._is_running = True
        self.structures = structures_db

    def stop(self):
        self._is_running = False

    def run(self):
        lastid = self.structures.database.get_lastrowid()
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        for num, result in enumerate(find_files(self.root_dir, exclude_dirs=EXCLUDED_NAMES,
                                                progress_callback=lambda percent: self.progress.emit(percent))):
            if self.stop:
                break
            if result.file_type == FileType.CIF:
                process_cif(lastid, result, self.structures)
            if result.file_type == FileType.RES:
                process_res(lastid, result, self.structures)
            lastid += 1
            #print(result)
        print(num)
            #self.progress.emit(num)
            #self.found.emit(result)
        self.progress.emit(0)
        print('finished')
        self.finished.emit()

