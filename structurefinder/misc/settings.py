from pathlib import Path

from PyQt5.QtCore import QSettings


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
