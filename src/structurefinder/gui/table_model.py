from __future__ import annotations

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


def _cell_column_positions() -> list[int]:
    """Return the data-row indices for a, b, c, alpha, beta, gamma if they are all visible."""
    cell_attrs = ['a', 'b', 'c', 'alpha', 'beta', 'gamma']
    visible = columns.visible_headers()  # ordered list of visible column names
    positions: list[int] = []
    for attr in cell_attrs:
        if attr in visible:
            # Data index is 1 + position in visible_headers (index 0 is the Id)
            positions.append(1 + visible.index(attr))
        else:
            return []  # Not all cell columns are visible
    return positions


def _make_cell_key(row: list, positions: list[int]) -> tuple[float, ...] | None:
    """Round the 6 cell values to 2 decimals and return as a hashable key."""
    vals: list[float] = []
    for pos in positions:
        try:
            v = float(row[pos])
            vals.append(round(v, 2))
        except (ValueError, TypeError, IndexError):
            return None
    if len(vals) != 6:
        return None
    return tuple(vals)


class _GroupNode:
    """Internal node used by GroupedStructuresModel."""

    __slots__ = ('children', 'key', 'label')

    def __init__(self, key: tuple[float, ...] | None, label: str) -> None:
        self.key = key
        self.label = label
        self.children: list[list] = []  # original data rows


class GroupedStructuresModel(QtCore.QAbstractItemModel):
    """Two-level tree model that groups structures by rounded unit-cell parameters."""

    def __init__(self, structures: list[list] | None = None, parent=None) -> None:
        super().__init__(parent)
        self._data: list[list] = structures or []
        self._groups: list[_GroupNode] = []
        self._rebuild_groups()

    # ------------------------------------------------------------------
    # Grouping logic
    # ------------------------------------------------------------------
    def _rebuild_groups(self) -> None:
        self.beginResetModel()
        self._groups.clear()
        positions = _cell_column_positions()

        groups_dict: dict[tuple[float, ...] | None, _GroupNode] = {}
        for row in self._data:
            key: tuple[float, ...] | None = None
            if positions:
                key = _make_cell_key(row, positions)
            if key not in groups_dict:
                if key is not None:
                    label = (
                        f"a={key[0]:.2f}  b={key[1]:.2f}  c={key[2]:.2f}  "
                        f"\u03b1={key[3]:.2f}  \u03b2={key[4]:.2f}  \u03b3={key[5]:.2f}"
                    )
                else:
                    label = "No cell"
                groups_dict[key] = _GroupNode(key, label)
            groups_dict[key].children.append(row)

        # Update labels with count and store as list
        for node in groups_dict.values():
            node.label = f"{node.label}  ({len(node.children)} structures)"
            self._groups.append(node)
        self.endResetModel()

    # ------------------------------------------------------------------
    # QAbstractItemModel interface
    # ------------------------------------------------------------------
    _PARENT_ID = 0  # internalId value for top-level (group) items

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            # Top-level: group node — internalId = 0
            return self.createIndex(row, column, self._PARENT_ID)
        # Child: encode the group row as internalId = group_row + 1
        group_row = parent.row()
        return self.createIndex(row, column, group_row + 1)

    def parent(self, index: QModelIndex = QModelIndex()) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        internal = index.internalId()
        if internal == self._PARENT_ID:
            # Top-level item — no parent
            return QModelIndex()
        group_row = internal - 1
        return self.createIndex(group_row, 0, self._PARENT_ID)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not parent.isValid():
            return len(self._groups)
        if parent.internalId() == self._PARENT_ID:
            # parent is a group node
            group_row = parent.row()
            if 0 <= group_row < len(self._groups):
                return len(self._groups[group_row].children)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not self._data:
            return 0
        return columns.number_of_visible_columns() + 1

    def data(self, index: QModelIndex, role: int | None = None) -> Any:
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        internal = index.internalId()
        col = index.column()
        if internal == self._PARENT_ID:
            # Group (parent) row
            group_row = index.row()
            if 0 <= group_row < len(self._groups):
                if col == 0:
                    return self._groups[group_row].label
            return None
        # Child row
        group_row = internal - 1
        if 0 <= group_row < len(self._groups):
            child_row = index.row()
            children = self._groups[group_row].children
            if 0 <= child_row < len(children):
                value = children[child_row][col]
                if col > 0:
                    colmethod = columns.col_from(col - 1)
                    if colmethod is not None:
                        return colmethod.string_method(value)
                return value
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                headers = columns.visible_header_names()
                if 0 <= section < len(headers):
                    return headers[section]
            elif orientation == Qt.Orientation.Vertical:
                return str(section + 1)
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def is_child_index(self, index: QModelIndex) -> bool:
        """Return True if the index is a child (structure) row, not a group parent."""
        return index.isValid() and index.internalId() != self._PARENT_ID

    def structure_id_from_index(self, index: QModelIndex) -> int | None:
        """Return the structure ID from a child index, or None for parent rows."""
        if not self.is_child_index(index):
            return None
        group_row = index.internalId() - 1
        if 0 <= group_row < len(self._groups):
            child_row = index.row()
            children = self._groups[group_row].children
            if 0 <= child_row < len(children):
                return children[child_row][0]
        return None
