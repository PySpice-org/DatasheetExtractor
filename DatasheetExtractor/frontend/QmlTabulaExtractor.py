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

__all__ = ['QmlTabulaExtractor']

####################################################################################################

from pathlib import Path
from typing import Any
import logging

import pandas as pd

from qtpy.QtCore import Property, Signal, Slot, QObject, Qt, QAbstractTableModel, QModelIndex
from qtpy.QtQml import QmlElement, QmlUncreatable

from DatasheetExtractor.backend.extractor.tabula import TabulaExtractor
from DatasheetExtractor.common.backup import backup_file
from .Runnable import Worker
from .PandasModel import PandasModel

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

QML_IMPORT_NAME = 'DatasheetExtractor'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0   # Optional

####################################################################################################

@QmlElement
@QmlUncreatable('QmlTabulaExtractor')
class QmlTabulaExtractor(QObject):

    _logger = _module_logger.getChild('QmlTabulaExtractor')

    SUFFIX = ".{page_number}.csv"
    SUFFIX_LENGTH_MAX = 256

    ##############################################

    def __init__(self) -> None:
        super().__init__()
        self._path = None
        self._page_number = None
        self._df = None
        self._table = PandasModel()
        self._suffix = self.SUFFIX
        self._suffix_error_message = ''

    ##############################################

    @property
    def path(self) -> str:
        return str(self._path)

    @path.setter
    def path(self, value: str) -> None:
        self._path = Path(value)

    ##############################################

    suffix_error_message_changed = Signal()

    @Property(str, notify=suffix_error_message_changed)
    def suffix_error_message(self) -> str:
        return self._suffix_error_message

    @suffix_error_message.setter
    def suffix_error_message(self, value: str) -> None:
        self._logger.info(f'"{self._suffix_error_message}" vs "{value}"')
        if self._suffix_error_message != value:
            self._suffix_error_message = value
            self.suffix_error_message_changed.emit()

    ##############################################

    suffix_changed = Signal()

    @Property(str, notify=suffix_changed)
    def suffix(self) -> str:
        return self._suffix

    @suffix.setter
    def suffix(self, value: str) -> None:
        self._logger.info(f'"{value}" vs "{self._suffix}"')
        if self._suffix != value:
            is_valid = True
            open_count = value.count('{')
            close_count = value.count('}')
            if len(value) > self.SUFFIX_LENGTH_MAX:
                is_valid = False
                message = 'too long suffix'
            elif open_count != close_count:
                is_valid = False
                message = '{ and } mismatch'
            elif 1 < open_count:
                is_valid = False
                message = 'more than one {'
            elif open_count:
                open_index = value.find('{')
                close_index = value.find('}')
                if value[open_index+1:close_index] != 'page_number':
                    is_valid = False
                    message = 'only {page_number} is allowed'
            if is_valid:
                self._suffix = value
                self.suffix_changed.emit()
                self.suffix_error_message = ''
            else:
                self._logger.warning(message)
                self._suffix = None
                self.suffix_error_message = message

    ##############################################

    @property
    def first_df(self) -> pd.DataFrame:
        return self._df[0]

    ##############################################

    # done = Signal()
    table_changed = Signal()

    # Fixme: 'QList<int>' ok ?
    @Slot(int, float, float, float, float, bool)
    def process_page_area(
            self,
            page_number: int,
            # guess: bool,
            top: float,
            left: float,
            bottom: float,
            right: float,
            lattice: bool = True,
            # to_csv: bool = False
    ) -> None:
        self._logger.info(f'page {page_number} [{left:3.0f}, {right:3.0f}]x[{top:3.0f}, {bottom:3.0f}] lattice {lattice}')
        from .Application import Application
        def job() -> None:
            _ = TabulaExtractor(self._path)
            data_frames = _.extract(
                page_number=page_number,
                guess=False,
                relative_area=(top, left, bottom, right),
                scaled_by_100=True,
                lattice=lattice,
                to_csv=False,
            )
            self._page_number = page_number
            self._df = data_frames
            self._table.update(data_frames[0])
            return f'{page_number}'

        worker = Worker(job)
        # worker.signals.result.connect(self.result)
        worker.signals.done.connect(self.table_changed)
        # worker.signals.progress.connect(self.progress_fn)

        Application.instance.thread_pool.start(worker)

    ##############################################

    # Use QObject type instead of PandasModel else
    #   QMetaProperty::read: Unable to handle unregistered datatype 'QAbstractTableModel*'
    #   for property 'QmlTabulaExtractor::table'
    @Property(QObject, constant=True)   # notify=table_changed
    def table(self) -> PandasModel:
        # if self._df:
        #     self._model = PandasModel(self.first_df)
        #     return self._model
        # else:
        #     return None
        return self._table

    @Property(str, notify=table_changed)
    def csv_table(self) -> str:
        if self._df:
            return self.first_df.to_csv()
        else:
            return ''

    ##############################################

    @Slot(result=str)
    def save(self) -> None:
        if self._suffix:
            suffix = self._suffix.format(page_number=self._page_number)
            path = self._path.parent.joinpath(self._path.stem + suffix)
            backup_file(path)
            self._logger.info(f"Write {path}")
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
            self.first_df.to_csv(path)
            return str(path)
        else:
            return ''
