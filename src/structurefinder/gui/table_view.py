import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Union, Dict, List, Literal

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from structurefinder import strf

from structurefinder.searcher.database_handler import default_columns



class HeaderContextMenu(QtWidgets.QHeaderView):
    columns_changed = pyqtSignal()

    def __init__(self,
                 parent: 'StructuresListTableView',
                 available_columns: List[str],
                 visible_columns: List[str]):
        super().__init__(QtCore.Qt.Horizontal, parent)
        self.table = parent
        self.available_columns = available_columns  # All possible columns
        self.visible_columns = visible_columns  # Currently displayed columns

    def contextMenuEvent(self, event):
        """
        Right-click menu for the horizontal header.
        """
        menu = QtWidgets.QMenu(self.table)
        for column_name in self.available_columns:
            action = QtWidgets.QAction(f"{column_name}", self.table)
            action.setCheckable(True)
            action.setChecked(column_name in self.visible_columns)
            action.triggered.connect(lambda checked, col=column_name: self.toggle_column(col, checked))
            menu.addAction(action)
        menu.exec_(event.globalPos())

    def toggle_column(self, column_name: str, show: bool) -> None:
        print(f'Column toggled: {column_name}, show: {show}')
        if show:
            self.visible_columns.append(column_name)
        else:
            self.visible_columns.remove(column_name)
        self.columns_changed.emit()


class StructuresListTableView(QtWidgets.QTableView):
    save_excel_triggered = pyqtSignal()
    open_save_path = pyqtSignal(str)

    # columns_changed = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.doubleClicked.connect(self._on_open_file_path)
        self.available_columns: List[str] = list(column_sources.keys())
        self.visible_columns: Dict[str, str] = default_columns.copy()
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setSectionsClickable(True)
        self.header_menu = HeaderContextMenu(self, self.available_columns, list(self.visible_columns.keys()))
        self.setHorizontalHeader(self.header_menu)
        self.header_menu.columns_changed.connect(self.set_visible_columns)

    def set_visible_columns(self):
        columns = {}
        for column_name in self.header_menu.visible_columns:
            columns.update({column_name: column_sources[column_name]})
        self.visible_columns = columns

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

    def refresh_data(self):
        """ Refresh table data based on currently visible columns. """
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = strf.StartStructureDB(db_file_name='./tests/test-data/test.sql')
    app.exec_()
