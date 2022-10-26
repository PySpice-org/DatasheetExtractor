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
import logging

from qtpy.QtCore import Property, Signal, Slot, QObject
from qtpy.QtQml import QmlElement, QmlUncreatable

from DatasheetExtractor.backend.extractor.tabula import TabulaExtractor
from .Runnable import Worker

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
        self._path = value

    ##############################################

    done = Signal()

    # Fixme: 'QList<int>' ok ?
    @Slot(int, int, int, int, int, bool)
    def process_page_area(
            self,
            page_number: int,
            top: float,
            left: float,
            bottom: float,
            right: float,
            lattice: bool = True,
            # to_csv: bool = False
    ) -> None:
        def job() -> None:
            _ = TabulaExtractor(self._path)
            data_frames = _.extract(
                page_number=page_number,
                guess=False,
                lattice=lattice,
                relative_area=(top, left, bottom, right),
            )
            self._result = data_frames
            return ''

        worker = Worker(job)
        # worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.done)
        # worker.signals.progress.connect(self.progress_fn)

        from .QmlApplication import Application
        Application.instance.thread_pool.start(worker)
