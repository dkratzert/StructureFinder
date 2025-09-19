import sys

from qtpy import QtWidgets, QtCore
from qtpy.QtCore import Qt, QModelIndex
from qtpy.QtSql import QSqlDatabase, QSqlTableModel, QSqlRelationalTableModel, QSqlRelation, QSqlRecord
from qtpy import QtWidgets


class Contacts(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QTableView Example")
        self.resize(815, 600)
        if not create_connection():
            sys.exit(1)
        # Set up the model
        self.model = ContactsModel()
        # Set up the view
        self.table = QtWidgets.QTableView()
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(0, 0)
        self.table.setModel(self.model.model)
        # self.table.resizeColumnsToContents()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(QtWidgets.QTableView.EditTrigger.NoEditTriggers)
        self.setCentralWidget(self.table)


class MyQSqlTableModel(QSqlTableModel):
    def __init__(self):
        super().__init__()
        self.order_column = 0
        self.sort_order = 0

    def relation(self, column: int) -> QSqlTableModel:
        print(column)
        return super().relationModel(column)

    def setRelation(self, column: int, relation: QSqlRelation) -> None:
        return super(MyQSqlTableModel, self).setRelation(column, relation)

    def orderByClause(self) -> str:
        order = "ASC"
        if self.sort_order == 1:
            order = "DESC"
        # return "GROUP BY Structure.Id, R.StructureId ORDER BY MAX(R.modification_time) {}".format(order)
        if self.order_column == 3:
            return "ORDER BY R.modification_time {}".format(order)
        else:
            return super().orderByClause()

    def sort(self, column: int, order: Qt.SortOrder) -> None:
        self.order_column = column
        self.sort_order = order
        return super().sort(column, order)

    def selectStatement(self) -> str:
        select = "SELECT distinct filename, dataname, path, modification_time FROM Structure " \
                 "join Residuals as R on Structure.Id = R.StructureId " \
                 "{}".format(self.orderByClause())
        print(select)
        return select


class ContactsModel:
    def __init__(self):
        self.model = self._create_model()

    @staticmethod
    def _create_model():
        """Create and set up the model."""
        table_model = MyQSqlTableModel()
        table_model.setTable("Structure")
        table_model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        table_model.select()
        print(table_model.selectStatement())
        headers = ("Filename", "Data name", "Path", "Date")
        for column_index, header in enumerate(headers):
            table_model.setHeaderData(column_index, QtCore.Qt.Orientation.Horizontal, header)
        return table_model


def create_connection():
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("structuredb.sqlite")
    if not con.open():
        QtWidgets.QMessageBox.critical(
            None,
            "QTableView Example - Error!",
            "Database Error: %s" % con.lastError().databaseText(),
        )
        return False
    return True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    if not create_connection():
        sys.exit(1)
    win = Contacts()
    win.show()
    sys.exit(app.exec())