from typing import Any, Union, List

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt

from structurefinder.searcher import worker
from structurefinder.searcher.database_handler import columns

archives = tuple([x.replace('*', '') for x in worker.archives])


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, structures=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data: List[List[str]] = structures or []

    @property
    def horizontalHeaders(self):
        return columns.visible_header_names()

    def data(self, index: QModelIndex, role: int = None) -> Union[str, None]:
        row, col = index.row(), index.column()
        value = self._data[row][col]
        if role == Qt.DisplayRole and col > 0:
            colmethod = columns.col_from(col - 1)
            return colmethod.string_method(value)
        if col == 0:
            return value

    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except IndexError:
                return False
        return super().setHeaderData(section, orientation, data, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except IndexError:
                pass
        return super().headerData(section, orientation, role)

    def rowCount(self, parent=None, *args, **kwargs):
        """
        The length of the outer list.
        """
        return len(self._data)

    def columnCount(self, parent=None, *args, **kwargs):
        """
        Takes the first sub-list, and returns
        the length (only works if all rows are an equal length)
        """
        if len(self._data) > 0:
            return columns.number_of_visible_columns() + 1
        else:
            return 0

    def setData(self, index: QModelIndex, value: Any, role: int = None) -> bool:
        row, col = index.row(), index.column()
        if not index:
            return False
        if index.isValid() and role == Qt.EditRole:
            self._data[row][col] = value
            return True
        return False

    def clear(self):
        self.resetInternalData()


class CustomProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_enabled = False

    def setFilterEnabled(self, enabled):
        self.filter_enabled = bool(enabled)
        self.invalidateFilter()

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        self.layoutAboutToBeChanged.emit()
        self.sourceModel()._data.sort(key=lambda x: x[column], reverse=True if order == Qt.DescendingOrder else False)
        self.layoutChanged.emit()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        if not self.filter_enabled:
            return True
        if not columns.path.visible:
            return False
        # Get the text of the row at sourceRow
        index = self.sourceModel().index(sourceRow, columns.path.position, sourceParent)
        text = self.sourceModel().data(index, Qt.DisplayRole)

        if text.endswith(archives):
            return False
        return True
