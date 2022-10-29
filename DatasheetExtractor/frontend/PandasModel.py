####################################################################################################
#
# DatasheetExtractor - A Python library to extract data from datasheet
# Copyright (C) 2022 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################################

__all__ = ['PandasModel']

####################################################################################################

from typing import Optional

import pandas as pd

from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex, QObject
from qtpy.QtQml import QmlElement, QmlUncreatable

####################################################################################################

QML_IMPORT_NAME = "DatasheEtextractor"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0

@QmlElement
@QmlUncreatable('PandasModel')
class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    ##############################################

    def __init__(self, dataframe: Optional[pd.DataFrame] = None, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        if dataframe is not None:
            self._dataframe = dataframe
        else:
            self._dataframe = pd.DataFrame([])

    ##############################################

    def clear(self) -> None:
        self.update(pd.DataFrame([]))

    ##############################################

    def update(self, dataframe: Optional[pd.DataFrame]) -> None:
        self._dataframe = dataframe
        self.modelReset.emit()

    ##############################################

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)
        return 0

    ##############################################

    def columnCount(self, parent: QModelIndex =QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0

    ##############################################

    def data(self, index: QModelIndex, role=Qt.ItemDataRole) -> str | None:
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        return None

    ##############################################

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> str | None:
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])
            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])
        return None

####################################################################################################

    ##############################################

    # def data(self, index, role):
    #     row = index.row()
    #     column = index.column()
    #     match role:
    #         case Qt.DisplayRole:
    #             return self._data[row][column]

    ##############################################

    # def roleNames():
    #     return {QtCore.Qt.DisplayRole: "display"}

    ##############################################

    # def setData(self, index, value, role=QtCore.Qt.EditRole):
    #     row = index.row()
    #     column = index.column()
    #     item = self._data[row][column]
    #     return False

    ##############################################

    # def headerData(self, section, orientation, role):
    #     if role == QtCore.Qt.DisplayRole:
    #         if orientation == QtCore.Qt.Horizontal:
    #             return self.h_headers[section]
    #         if orientation == QtCore.Qt.Vertical:
    #             return self.v_headers[section]

    ##############################################

    # def flags(self, index):
    #     return (
    #         QtCore.Qt.ItemIsEditable
    #         | QtCore.Qt.ItemIsEnabled
    #         | QtCore.Qt.ItemIsSelectable
    #         | QtCore.Qt.ItemIsDragEnabled
    #         | QtCore.Qt.ItemIsDropEnabled
    #     )
