from typing import List, Any
from PyQt5.QtCore import Qt, QAbstractTableModel


class ConfigurableTableModel(QAbstractTableModel):
    def __init__(self, users: List[Any], columns: List[dict]):
        super().__init__()
        self.users = users
        self.columns = columns

    def rowCount(self, parent=None) -> int:
        return len(self.users)

    def columnCount(self, parent=None) -> int:
        return len(self.columns)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            user = self.users[index.row()]
            getter = self.columns[index.column()]["getter"]
            return getter(user)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]["header"]
        return None

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder):
        self.layoutAboutToBeChanged.emit()
        getter = self.columns[column]["getter"]
        self.users.sort(key=getter, reverse=(order == Qt.DescendingOrder))
        self.layoutChanged.emit()

    def refresh(self, users: List[Any]):
        self.beginResetModel()
        self.users = users
        self.endResetModel()