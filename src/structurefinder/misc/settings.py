from collections import namedtuple
from pathlib import Path

from PyQt5.QtCore import QSettings, QPoint, QSize

Position = namedtuple('Position', 'size, position, maximized')


class StructureFinderSettings():
    def __init__(self):
        self.software_name = 'StructureFinder'
        self.organization = 'DK'
        self.settings = QSettings(self.organization, self.software_name)
        self.settings.setDefaultFormat(QSettings.IniFormat)

    def save_current_work_dir(self, dir: str) -> None:
        """
        Saves the last directory where we saved a database.
        """
        self.settings.beginGroup("WorkDir")
        self.settings.setValue('dir', dir)
        self.settings.endGroup()

    def load_last_workdir(self) -> str:
        self.settings.beginGroup('WorkDir')
        lastdir = self.settings.value("dir", type=str)
        if not Path(lastdir).exists():
            lastdir = './'
        self.settings.endGroup()
        return lastdir

    def save_current_index_dir(self, dir: str) -> None:
        """
        Saves the directory where we last indexed files.
        """
        self.settings.beginGroup("IndexDir")
        self.settings.setValue('dir', dir)
        self.settings.endGroup()

    def load_last_indexdir(self) -> str:
        self.settings.beginGroup('IndexDir')
        lastdir = self.settings.value("dir", type=str)
        if not Path(lastdir).exists():
            lastdir = './'
        self.settings.endGroup()
        return lastdir

    def save_ccdc_exe_path(self, path: str) -> None:
        """
        Saves the last directory where we saved a database.
        """
        self.settings.beginGroup("CCDC")
        self.settings.setValue('exepath', path)
        self.settings.endGroup()

    def load_ccdc_exe_path(self) -> str:
        self.settings.beginGroup('CCDC')
        exe_path = self.settings.value("exepath", type=str)
        if not Path(exe_path).exists() or not Path(exe_path).is_file():
            exe_path = ''
        self.settings.endGroup()
        return exe_path

    def save_window_position(self, position: QPoint, size: QSize, maximized: bool) -> None:
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("position", position)
        self.settings.setValue("size", size)
        self.settings.setValue('maximized', maximized)
        self.settings.endGroup()

    def load_window_position(self) -> 'Position':
        """
        Loads window position information and sets default values if no configuration exists.
        """
        self.settings.beginGroup("MainWindow")
        pos = self.settings.value("position", type=QPoint)
        size = self.settings.value("size", type=QSize)
        size = size if size.width() > 0 else QSize(1000, 950)
        pos = pos if pos.x() > 0 else QPoint(20, 20)
        maximized = self.settings.value('maximized')
        maxim = False
        if isinstance(maximized, str):
            if eval(maximized.capitalize()):
                maxim = True
            else:
                maxim = False
        if maximized is None:
            # In this case, there was no saved setting
            maxim = True
        self.settings.endGroup()
        return Position(size=size, position=pos, maximized=maxim)
