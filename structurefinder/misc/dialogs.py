import ctypes
from pathlib import Path

from PyQt5.QtWidgets import QMainWindow, QMessageBox

from structurefinder.misc.version import VERSION


def bug_found_warning(logfile) -> None:
    window = QMainWindow()
    text = 'Congratulations, you found a bug in ' \
           'StructureFinder!<br>Please send the file <br>"{}" <br>to Daniel Kratzert:  ' \
           '<a href="mailto:dkratzert@gmx.de?subject=StructureFinder version {} crash report">' \
           'dkratzert@gmx.de</a><br>' \
           'If possible, the corresponding CIF file is also desired.'.format(logfile.absolute(), VERSION)
    QMessageBox.warning(window, 'Warning', text)
    window.show()


def do_update_program(version):
    updater_exe = Path(__file__).parent.parent.parent.joinpath('update.exe')  # parent path of gui -> main dir
    args = ['-v', version,
            '-p', 'structurefinder']
    # Using this, because otherwise I can not write to the program dir:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", updater_exe, " ".join(args), None, 1)
