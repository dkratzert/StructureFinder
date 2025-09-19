from collections import namedtuple
from pathlib import Path

from qtpy import QtCore
from qtpy.QtCore import QSettings, QPoint, QSize

Position = namedtuple('Position', 'size, position, maximized')


class StructureFinderSettings:
    def __init__(self):
        self.software_name = 'StructureFinder'
        self.organization = 'DK'
        self.settings = QSettings(self.organization, self.software_name)
        self.settings.setDefaultFormat(QSettings.Format.IniFormat)

    def save_current_work_dir(self, dir: str) -> None:
        """
        Saves the last directory where we saved a database.
        """
        self.settings.beginGroup("WorkDir")
        self.settings.setValue('dir', dir)
        self.settings.endGroup()

    def load_last_workdir(self) -> str:
        self.settings.beginGroup('WorkDir')
        last_dir = self.settings.value("dir", type=str)
        self.settings.endGroup()
        last_dir = self._find_dir(last_dir)
        return last_dir

    def _find_dir(self, last_dir):
        try:
            if not Path(last_dir).exists():
                last_dir = './'
        except OSError:
            last_dir = './'
        return last_dir

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
        self.settings.endGroup()
        lastdir = self._find_dir(lastdir)
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

    def load_visible_headers(self) -> list[str]:
        self.settings.beginGroup("Headers")
        headers = self.settings.value("visible")
        # print(f'Loaded headers: {headers}')
        self.settings.endGroup()
        return headers or []

    def save_window_position(self, position: QPoint, size: QSize, maximized: bool) -> None:
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("position", position)
        self.settings.setValue("size", size)
        self.settings.setValue('maximized', maximized)
        self.settings.endGroup()

    def save_visible_headers(self, columns: list[str]):
        self.settings.beginGroup("Headers")
        self.settings.setValue("visible", columns)
        self.settings.endGroup()
        # print(f'Saved visible headers: {columns}')

    def save_column_state(self, state: QtCore.QByteArray) -> None:
        self.settings.beginGroup("Headers")
        self.settings.setValue("column_order", state)
        self.settings.endGroup()

    def load_column_state(self) -> QtCore.QByteArray:
        self.settings.beginGroup("Headers")
        state: QtCore.QByteArray = self.settings.value("column_order", None)
        self.settings.endGroup()
        return state

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
