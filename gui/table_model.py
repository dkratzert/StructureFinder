from typing import Any

from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex, Qt


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, structures=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = structures or []

    def data(self, index: QModelIndex, role: int = None):
        row, col = index.row(), index.column()
        value = self._data[row][col]
        if row == 0:
            return
        if col == 0:
            return 
        if role == Qt.DisplayRole:
            if isinstance(value, bytes):
                return value.decode('ascii')
            else:
                return value
        #return value

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
            return len(self._data[0])
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