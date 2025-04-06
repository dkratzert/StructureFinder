from PyQt5.QtCore import QObject, QThread, pyqtSignal

from structurefinder.searcher.crawler2 import Result, FileType, find_files, EXCLUDED_NAMES


class SearchWorker(QObject):
    progress = pyqtSignal(int)
    found = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, root_dir):
        super().__init__()
        self.stop = False
        self.root_dir = root_dir
        self.exclude_dirs = EXCLUDED_NAMES
        self._is_running = True

    def stop(self):
        self._is_running = False

    def run(self):
        for num, result in enumerate(find_files(self.root_dir, exclude_dirs=EXCLUDED_NAMES,
                                                progress_callback=lambda percent: self.progress.emit(percent))):
            if self.stop:
                break
            #print(result)
            #print(num)
            #self.progress.emit(num)
            #self.found.emit(result)
        self.progress.emit(0)
        print('finished')
        self.finished.emit()

