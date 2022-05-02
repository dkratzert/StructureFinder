from PyQt5 import QtCore

from searcher import filecrawler
from searcher.database_handler import StructureTable


class Worker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)

    def __init__(self, searchpath: str, add_res_files: bool, add_cif_files: bool, lastid: int,
                 structures: StructureTable):
        super().__init__()
        self.searchpath = searchpath
        self.add_res_files = add_res_files
        self.add_cif_files = add_cif_files
        self.structures = structures
        self.lastid = lastid

    def index_files(self):
        filecrawler.put_files_in_db(self=None, searchpath=self.searchpath, structures=self.structures,
                                    fillres=self.add_res_files,
                                    fillcif=self.add_cif_files, lastid=self.lastid)
        self.finished.emit()
