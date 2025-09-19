from typing import Any

from qtpy import QtCore
from qtpy.QtCore import QModelIndex, Qt

import structurefinder.searcher.constants
from structurefinder.searcher.database_handler import columns

archives = tuple([x.replace("*", "") for x in structurefinder.searcher.constants.archives])


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, structures=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data: list[list[str]] = structures or []

    @property
    def horizontalHeaders(self):
        return columns.visible_header_names()

    def data(self, index: QModelIndex, role: int | None = None) -> str | None:
        if not index.isValid() or role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        row, col = index.row(), index.column()
        value = self._data[row][col]
        if role == QtCore.Qt.ItemDataRole.DisplayRole and col > 0:
            colmethod = columns.col_from(col - 1)
            return colmethod.string_method(value)
        if col == 0:
            return value
        return None

    def setHeaderData(self, section, orientation, data, role=Qt.ItemDataRole.EditRole):
        if orientation == Qt.Orientation.Horizontal and role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except IndexError:
                return False
        return super().setHeaderData(section, orientation, data, role)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self.horizontalHeaders[section]
            elif orientation == QtCore.Qt.Orientation.Vertical:
                return str(section + 1)
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

    def setData(self, index: QModelIndex, value: Any, role: int | None = None) -> bool:
        row, col = index.row(), index.column()
        if not index:
            return False
        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:
            self._data[row][col] = value
            return True
        return False

    def clear(self):
        self.resetInternalData()

    def sort(self, column: int, order: Qt.SortOrder = ...):
        def convert(value):
            try:
                return float(value)
            except ValueError:
                return value.casefold() if isinstance(value, str) else value

        self.layoutAboutToBeChanged.emit()
        self._data.sort(
            key=lambda row: convert(row[column]),
            reverse=(order == QtCore.Qt.SortOrder.DescendingOrder),
        )
        self.layoutChanged.emit()


class CustomProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_enabled = False

    def setFilterEnabled(self, enabled):
        self.filter_enabled = bool(enabled)
        self.invalidateFilter()

    def sort(self, column: int, order: Qt.SortOrder = ...):
        self.layoutAboutToBeChanged.emit()
        self.sourceModel()._data.sort(
            key=lambda row: columns.col_from(column - 1).data_type(row[column]),
            reverse=(order == QtCore.Qt.SortOrder.DescendingOrder),
        )
        self.layoutChanged.emit()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        if not self.filter_enabled:
            return True
        if not columns.path.visible:
            return False
        # Get the text of the row at sourceRow
        index = self.sourceModel().index(sourceRow, columns.path.position, sourceParent)
        text = self.sourceModel().data(index, QtCore.Qt.ItemDataRole.DisplayRole)

        if text.endswith(archives):
            return False
        return True
