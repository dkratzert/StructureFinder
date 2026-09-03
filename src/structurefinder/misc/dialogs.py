from __future__ import annotations

import os
import threading
import traceback
from pathlib import Path

from qtpy import QtCore
from qtpy.QtCore import QProcess
from qtpy.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog, QWidget

from structurefinder.misc.selfupdate import (ElevationRefused, UpdateCancelled, UpdateError, can_self_update,
                                             download_installer, start_exit_watchdog, start_installer,
                                             start_user_installer, user_installation_directory)
from structurefinder.misc.version import VERSION

# Keeps the running downloads alive, a local variable would be garbage collected:
_running_updates: set = set()


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


class InstallerDownload:
    """Downloads the StructureFinder installer in a background thread.

    Not a single Qt object is touched from that thread; the GUI polls the state of the
    download with a timer instead (see :func:`update_installation`).
    """

    def __init__(self, version: str) -> None:
        self.version = version
        self.setup_file: Path | None = None
        self.error = ''
        self.finished = False
        self._lock = threading.Lock()
        self._received = 0
        self._total = 0
        self._cancelled = False

    def start(self) -> None:
        threading.Thread(target=self.run, daemon=True).start()

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def progress(self) -> tuple[int, int]:
        with self._lock:
            return self._received, self._total

    def _report_progress(self, received: int, total: int) -> None:
        with self._lock:
            self._received = received
            self._total = total

    def run(self) -> None:
        try:
            self.setup_file = download_installer(self.version,
                                                 progress=self._report_progress,
                                                 should_cancel=lambda: self._cancelled)
        except UpdateCancelled:
            pass
        except UpdateError as err:
            self.error = str(err)
        except Exception as err:  # The dialog would wait forever for a thread that died:
            traceback.print_exc()
            self.error = f'The installer could not be downloaded:\n{err!r}'
        finally:
            self.finished = True


def do_update_program(version: str, parent: QWidget | None = None) -> None:
    if can_self_update():
        update_installation(version, parent)
    else:
        print('No update available.')


def update_installation(version: str, parent: QWidget | None = None) -> None:
    """Download the installer and hand the installation directory over to it."""
    progress_dialog = QProgressDialog('Downloading the StructureFinder installer...', 'Cancel', 0, 100, parent)
    progress_dialog.setWindowTitle('StructureFinder update')
    progress_dialog.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
    progress_dialog.setAutoClose(False)
    progress_dialog.setAutoReset(False)
    progress_dialog.setMinimumDuration(0)
    progress_dialog.setValue(0)
    downloader = InstallerDownload(version)
    # Everything below runs in the GUI thread, driven by this timer:
    timer = QtCore.QTimer(progress_dialog)
    timer.setInterval(200)
    # Plain local variables would be garbage collected while the thread is downloading:
    running_update = (downloader, progress_dialog)

    def show_progress() -> None:
        received, total = downloader.progress
        if total:
            progress_dialog.setRange(0, 100)
            progress_dialog.setValue(int(100 * received / total))
        elif received:
            # Without a content-length there is nothing to calculate a percentage from:
            progress_dialog.setRange(0, 0)
        if received and received == total:
            progress_dialog.setLabelText('Verifying the downloaded installer...')
        else:
            progress_dialog.setLabelText(f'Downloading the StructureFinder installer... '
                                         f'({received / 1024 ** 2:.1f} MB)')

    def on_failed(message: str) -> None:
        progress_dialog.close()
        show_general_warning(parent, warn_text='The update failed.', info_text=message,
                             window_title='StructureFinder update')

    def on_downloaded(setup_file: Path) -> None:
        progress_dialog.setLabelText('Closing StructureFinder for the installation...')
        progress_dialog.setRange(0, 100)
        progress_dialog.setValue(100)
        QApplication.processEvents()
        release_installation_directory()
        try:
            start_installer(setup_file)
        except ElevationRefused as err:
            progress_dialog.close()
            if not install_into_user_directory(setup_file, str(err), parent):
                return
        except UpdateError as err:
            on_failed(str(err))
            return
        progress_dialog.close()
        quit_application()

    def check_download() -> None:
        show_progress()
        if not downloader.finished:
            return
        timer.stop()
        _running_updates.discard(running_update)
        if downloader.error:
            on_failed(downloader.error)
        elif downloader.setup_file is not None:
            on_downloaded(downloader.setup_file)
        else:
            progress_dialog.close()

    timer.timeout.connect(check_download)
    progress_dialog.canceled.connect(downloader.cancel)
    _running_updates.add(running_update)
    downloader.start()
    progress_dialog.show()
    timer.start()


def install_into_user_directory(setup_file: Path, reason: str, parent: QWidget | None = None) -> bool:
    """Offer the per-user installation to accounts without administrator rights."""
    question = QMessageBox(parent)
    question.setWindowTitle('StructureFinder update')
    question.setIcon(QMessageBox.Icon.Question)
    question.setText('StructureFinder can be installed in your personal folder instead.')
    question.setInformativeText(f'{reason}\n\n'
                                f'Install StructureFinder into\n{user_installation_directory()}\ninstead? '
                                f'This needs no administrator rights.\n\n'
                                f'The current installation stays where it is. Start the new StructureFinder '
                                f'from your personal start menu entry afterwards.')
    question.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    question.setDefaultButton(QMessageBox.StandardButton.Yes)
    if question.exec() != QMessageBox.StandardButton.Yes:
        return False
    try:
        start_user_installer(setup_file)
    except UpdateError as err:
        show_general_warning(parent, warn_text='The update failed.', info_text=str(err),
                             window_title='StructureFinder update')
        return False
    return True


def release_installation_directory() -> None:
    """Kill child processes, they may lock their executable in the installation dir."""
    app = QApplication.instance()
    if app is None:
        return
    for widget in app.topLevelWidgets():
        for process in widget.findChildren(QProcess):
            if process.state() != QProcess.ProcessState.NotRunning:
                process.kill()
                process.waitForFinished(3000)


def quit_application() -> None:
    """Leave StructureFinder so that the installer can replace all files."""
    start_exit_watchdog()
    app = QApplication.instance()
    if app is None:
        os._exit(0)
    app.closeAllWindows()
    app.quit()


def show_general_warning(parent: QWidget | None, warn_text: str = '', info_text: str = '',
                         window_title: str = ' ') -> None:
    box = QMessageBox(parent)
    box.setWindowTitle(window_title)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setText(warn_text)
    if info_text:
        box.setInformativeText(info_text)
    box.exec()


if __name__ == '__main__':
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle('StructureFinder update test')
    window.resize(300, 100)
    window.show()
    # Launches the real update dialog: it downloads the installer of this version, verifies it
    # and (on a Windows installation) starts it. Change the version to test another release.
    update_installation(str(VERSION), parent=window)
    sys.exit(app.exec())
