from typing import Union

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from structurefinder.gui.table_model import Column


class StructuresListTableView(QtWidgets.QTableView):
    save_excel_triggered = pyqtSignal()
    open_save_path = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.doubleClicked.connect(self._on_open_file_path)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        context_menu = QtWidgets.QMenu(self)
        save_excel = context_menu.addAction("Save as Excel File")
        context_menu.addAction(save_excel)
        open_path = context_menu.addAction("Open file path")
        context_menu.addAction(open_path)
        save_excel.triggered.connect(self._on_save_excel)
        open_path.triggered.connect(self._on_open_file_path)
        context_menu.popup(QCursor.pos())

    def _on_save_excel(self):
        self.save_excel_triggered.emit()

    def get_field_content(self, row: int, col: int) -> Union[str, int]:
        model = self.model()
        source_index = model.index(row, col)
        content = model.data(source_index)
        return content

    def _on_open_file_path(self) -> None:
        try:
            path_data = self.get_field_content(self.currentIndex().row(), Column.PATH)
        except IndexError:
            path_data = ''
        self.open_save_path.emit(path_data)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            pass
        super().mousePressEvent(e)
