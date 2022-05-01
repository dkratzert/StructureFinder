import time

from PyQt5 import QtCore


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def index_files(self):
        for i in range(5):
            time.sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()
