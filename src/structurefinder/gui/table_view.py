from __future__ import annotations

import sys

from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QCursor

from structurefinder import strf
from structurefinder.searcher.database_handler import columns


class CustomHorizontalHeaderView(QtWidgets.QHeaderView):
    columns_changed = Signal(str)

    def __init__(self, parent: StructuresListTableView):
        super().__init__(QtCore.Qt.Orientation.Horizontal, parent)
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
        menu.setStyleSheet("""
                QMenu {
                    background-color: #f0f0f0;
                    color: black;
                }
                QMenu::item:selected {
                    background-color: #3874f2;
                    color: white;
                }
            """)
        for column_name in self.available_columns:
            action = QtGui.QAction(f"{column_name}", self.table)
            action.setCheckable(True)
            action.setChecked(columns.is_visible(column_name))
            action.triggered.connect(lambda checked, col=column_name: self.toggle_column(col, checked))
            menu.addAction(action)
        menu.exec(event.globalPos())

    def toggle_column(self, column_name: str, show: bool) -> None:
        if show:
            getattr(columns, column_name).visible = True
        else:
            getattr(columns, column_name).visible = False
        self.columns_changed.emit(column_name)

    def reset_sorting(self):
        """Resets the sorting of the table."""
        self.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        self.table.model().sort(-1)


class StructuresListTableView(QtWidgets.QTableView):
    save_excel_triggered = Signal()
    open_save_path = Signal(str)

    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self.doubleClicked.connect(self._on_open_file_path)
        self.setSortingEnabled(True)
        self.header_menu = CustomHorizontalHeaderView(self)
        self.header_menu.setSectionsClickable(True)
        self.setHorizontalHeader(self.header_menu)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        context_menu = QtWidgets.QMenu(self)
        context_menu.setStyleSheet("""
                QMenu {
                    background-color: #f0f0f0;
                    color: black;
                }
                QMenu::item:selected {
                    background-color: #3874f2;
                    color: white;
                }
            """)
        save_excel = context_menu.addAction("Save as Excel File")
        context_menu.addAction(save_excel)
        open_path = context_menu.addAction("Open file path")
        context_menu.addAction(open_path)
        save_excel.triggered.connect(self._on_save_excel)
        open_path.triggered.connect(self._on_open_file_path)
        context_menu.popup(QCursor.pos())

    def _on_save_excel(self):
        self.save_excel_triggered.emit()

    def get_field_content(self, row: int, col: int) -> str | int:
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
        if e.button() == Qt.MouseButton.RightButton:
            pass
        super().mousePressEvent(e)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = strf.StartStructureDB(db_file_name='./tests/test-data/test.sql')
    app.exec()
