import sys

import requests
from qtpy.QtCore import QThread, Signal

from structurefinder.misc.version import VERSION


class MyDownloader(QThread):
    progress = Signal(str)
    failed = Signal(int)
    finished = Signal(bytes)

    def __init__(self, parent, url: str):
        super().__init__(parent=parent)
        self.url = url

    def run(self):
        try:
            self.download(self.url)
        except requests.RequestException as e:
            print('Could not connect to download server')
            print(e)

    def print_status(self, status: str) -> None:
        # print(status)
        pass

    def failed_to_download(self, status_code: int):
        print('Failed to download: {}'.format(self.url))
        print('HTTP status was {}'.format(status_code))

    def download(self, full_url: str) -> bytes:
        headers = {
            'User-Agent': f'StructureFinder v{VERSION} ({sys.platform})',
        }
        # self.progress.emit('Starting download: {}'.format(full_url))
        response = requests.get(full_url, stream=True, headers=headers, timeout=5)
        if response.status_code != 200:
            # noinspection PyUnresolvedReferences
            self.failed.emit(response.status_code)
            # noinspection PyUnresolvedReferences
            self.finished.emit(b'')
            return b''
        self.finished.emit(response.content)
        return response.content


if __name__ == "__main__":
    from qtpy.QtWidgets import QWidget
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = QWidget()
    w.show()


    def foo(bar: bytes):
        print(bar.decode('ascii'))


    upd = MyDownloader(parent=None, url="https://dkratzert.de/files/structurefinder/version.txt")
    upd.finished.connect(foo)
    upd.failed.connect(upd.failed_to_download)
    upd.progress.connect(upd.print_status)
    upd.start()
    sys.exit(app.exec())
