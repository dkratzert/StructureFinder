from PyQt5.QtCore import QSettings


class StructureFinderSettings():
    def __init__(self):
        self.software_name = 'StructureFinder'
        self.organization = 'DK'
        self.settings = QSettings(self.organization, self.software_name)
        self.settings.setDefaultFormat(QSettings.IniFormat)

    def save_current_dir(self, dir: str) -> None:
        """
        Saves the current work directory of the Program.
        :param dir: Directory as string
        """
        self.settings.beginGroup("WorkDir")
        self.settings.setValue('dir', dir)
        self.settings.endGroup()

    def load_last_workdir(self) -> str:
        self.settings.beginGroup('WorkDir')
        lastdir = self.settings.value("dir", type=str)
        if not lastdir:
            lastdir = './'
        self.settings.endGroup()
        return lastdir