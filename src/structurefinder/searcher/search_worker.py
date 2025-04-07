from PyQt5.QtCore import QObject, pyqtSignal

from structurefinder.searcher.crawler2 import EXCLUDED_NAMES, FileType, find_files
from structurefinder.searcher.database_handler import StructureTable
from structurefinder.strf_cmd import process_cif, process_res


class SearchWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, root_dir: str, structures_db: StructureTable) -> None:
        super().__init__()
        self.stop = False
        self.root_dir = root_dir
        self.exclude_dirs = EXCLUDED_NAMES
        self.structures = structures_db

    def stop(self):
        self.stop = True
        print('Stopping index worker...')

    def run(self):
        lastid = self.structures.database.get_lastrowid()
        if not lastid:
            lastid = 1
        else:
            lastid += 1
        for num, result in enumerate(find_files(self.root_dir, exclude_dirs=EXCLUDED_NAMES,
                                                progress_callback=lambda percent: self.progress.emit(percent))):
            if self.stop:
                print('Stopped.')
                break
            if result.file_type == FileType.CIF:
                if process_cif(lastid, result, self.structures):
                    lastid += 1
            if result.file_type == FileType.RES:
                if process_res(lastid, result, self.structures):
                    lastid += 1
            # print(result)
            # print(num)
            self.progress.emit(num)
        self.progress.emit(0)
        print('finished')
        self.finished.emit()
