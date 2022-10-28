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

# from pathlib import Path
from typing import Any
import logging

from qtpy.QtCore import Property, Signal, Slot, QObject, Qt, QAbstractTableModel, QModelIndex
from qtpy.QtQml import QmlElement, QmlUncreatable

from DatasheetExtractor.backend.extractor.tabula import TabulaExtractor
from .Runnable import Worker
from .PandasModel import PandasModel

####################################################################################################

QML_IMPORT_NAME = 'DatasheetExtractor'
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0   # Optional

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

# @QmlElement
# @QmlUncreatable
class QmlTabulaExtractor(QObject):

    _logger = _module_logger.getChild('QmlTabulaExtractor')

    ##############################################

    def __init__(self) -> None:
        super().__init__()
        self._path = None
        self._result = None

    ##############################################

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = str(value)

    ##############################################

    # @Property(str)
    @Slot(result=str)
    def csv_table(self) -> str:
        if self._result:
            # return self._result[0]
            return self._result[0].to_csv()
        else:
            return ''

    ##############################################

    table_changed = Signal()

    # QMetaProperty::read: Unable to handle unregistered datatype 'QAbstractTableModel*' for property 'QmlTabulaExtractor::table'
    @Property(PandasModel, notify=table_changed)
    def table(self) -> PandasModel:
        if self._result:
            self._model = PandasModel(self._result[0])
            return self._model
        else:
            return None

    ##############################################

    # result = Signal(str)
    done = Signal()

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
            self._result = data_frames
            Application.instance._table.update(data_frames[0])
            return f'{page_number}'

        worker = Worker(job)
        # worker.signals.result.connect(self.result)
        worker.signals.done.connect(self.done)
        # worker.signals.progress.connect(self.progress_fn)

        Application.instance.thread_pool.start(worker)
