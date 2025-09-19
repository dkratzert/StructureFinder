import ctypes
import os
from pathlib import Path

from qtpy.QtWidgets import QMainWindow, QMessageBox

from structurefinder.misc.version import VERSION


def bug_found_warning(logfile) -> None:
    window = QMainWindow()
    title = 'Congratulations, you found a bug in StructureFinder!'
    text = (f'<br>Please send the file <br><br>'
            f'<a href=file:{os.sep * 2}{logfile.resolve()}>{logfile.resolve()}</a> '
            f'<br><br>to Daniel Kratzert: '
            f'<a href="mailto:dkratzert@gmx.de?subject=StructureFinder version {VERSION} crash report">'
            f'dkratzert@gmx.de</a><br>')
    box = QMessageBox(parent=window)
    box.setWindowTitle('Warning')
    box.setText(title)
    box.setInformativeText(text)
    box.exec()
    window.show()


def do_update_program(version: str):
    # parent path of gui -> main dir:
    updater_exe = str(Path(__file__).parent.parent.parent.joinpath('update.exe'))
    args = ['-v', version,
            '-p', 'structurefinder']
    # Using this, because otherwise I can not write to the program dir:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", updater_exe, " ".join(args), None, 1)
