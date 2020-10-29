from PyQt5.QtWidgets import QMainWindow, QMessageBox

from misc.version import VERSION


def bug_found_warning(logfile) -> None:
    window = QMainWindow()
    text = 'Congratulations, you found a bug in ' \
           'StructureFinder!<br>Please send the file <br>"{}" <br>to Daniel Kratzert:  ' \
           '<a href="mailto:dkratzert@gmx.de?subject=FinalCif version {} crash report">' \
           'dkratzert@gmx.de</a><br>' \
           'If possible, the corresponding CIF file is also desired.'.format(logfile.absolute(), VERSION)
    QMessageBox.warning(window, 'Warning', text)
    window.show()