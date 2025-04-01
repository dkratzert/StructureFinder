import sys
from typing import Union

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from structurefinder import strf
from structurefinder.searcher.database_handler import columns


class HeaderContextMenu(QtWidgets.QHeaderView):
    columns_changed = pyqtSignal(str)

    def __init__(self, parent: 'StructuresListTableView'):
        super().__init__(QtCore.Qt.Horizontal, parent)
        self.table = parent
        self.available_columns = columns.all_column_names
        self.setSortIndicatorShown(True)
        self.setSectionsMovable(True)  # Allow users to drag & drop column headers
        self.setDragEnabled(True)

    def contextMenuEvent(self, event):
        """
        Right-click menu for the horizontal header.
        """
        menu = QtWidgets.QMenu(self.table)
        for column_name in self.available_columns:
            action = QtWidgets.QAction(f"{column_name}", self.table)
            action.setCheckable(True)
            action.setChecked(columns.is_visible(column_name))
            action.triggered.connect(lambda checked, col=column_name: self.toggle_column(col, checked))
            menu.addAction(action)
        menu.exec_(event.globalPos())

    def toggle_column(self, column_name: str, show: bool) -> None:
        if show:
            getattr(columns, column_name).visible = True
        else:
            getattr(columns, column_name).visible = False
        self.columns_changed.emit(column_name)

    def reset_sorting(self):
        """Resets the sorting of the table."""
        self.setSortIndicator(-1, Qt.AscendingOrder)
        self.table.model().sort(-1)


class StructuresListTableView(QtWidgets.QTableView):
    save_excel_triggered = pyqtSignal()
    open_save_path = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.doubleClicked.connect(self._on_open_file_path)
        self.setSortingEnabled(True)
        self.header_menu = HeaderContextMenu(self)
        self.header_menu.setSectionsClickable(True)
        self.setHorizontalHeader(self.header_menu)

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
            path_data = self.get_field_content(self.currentIndex().row(), columns.path.position)
        except IndexError:
            path_data = ''
        self.open_save_path.emit(path_data)

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.RightButton:
            pass
        super().mousePressEvent(e)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = strf.StartStructureDB(db_file_name='./tests/test-data/test.sql')
    app.exec_()
